from db import cursor,conn
from psycopg2.extras import execute_batch
from itertools import combinations

def deleteData():
    cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    AND table_name != 'spatial_ref_sys';
    """)
    tables = [t[0] for t in cursor.fetchall()]
    for t in tables:
        cursor.execute("""DROP TABLE {0};""".format(t))
    conn.commit()

def deleteRegionalTable():
    cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    AND table_name != 'spatial_ref_sys'
    AND table_name != 'events';
    """)
    tables = [t[0] for t in cursor.fetchall()]
    for t in tables:
        cursor.execute("""DROP TABLE {0};""".format(t))
    conn.commit()

def loadData(all_instances):
    query ="""
    CREATE TABLE events (
        id VARCHAR(64),
        event VARCHAR(64),
        location geography(POINT)
    )
    """
    cursor.execute(query)
    query = """
    INSERT INTO events VALUES
    (%s,%s,'POINT(%s %s)')
    """
    execute_batch(cursor,query,all_instances)
    conn.commit()

def createRegionalTable(box):
    query="""
    SELECT e.id,e.event,ST_X(e.location::geometry) as X,ST_Y(e.location::geometry) as Y
    FROM events as e WHERE 
    ST_Covers(ST_MAKEENVELOPE({2},{3},{0},{1},4326),e.location::geometry)
    """.format(*box)
    cursor.execute(query)
    res = cursor.fetchall()
    instances = {}
    events = set()
    events_count = {}
    for e in res:
        events.add(e[0])
        try:
            instances[e[0]].append((e[1],float(e[2]),float(e[3])))
            events_count[e[0]] +=1
        except KeyError:
            instances[e[0]] = [(e[1],float(e[2]),float(e[3]))]
            events_count[e[0]] = 1
    for event,data in instances.items():
        query = """CREATE TABLE {0} (
        event VARCHAR(64),
        location geography(POINT))
        """.format((event))
        cursor.execute(query)
        query = """
        INSERT INTO {0} VALUES
        (%s,'POINT(%s %s)')
        """.format((event))
        execute_batch(cursor,query,data)
        cursor.execute("""
        CREATE INDEX index_{0} ON {0} USING gist (location);
        """.format((event)))
    conn.commit()
    return events,events_count,instances

def spatialJoin(h,events):
    table = {}
    linePoints = []
    for tup in [sorted(comb) for comb in combinations(events, 2)]:
        create="""CREATE TABLE {0}{1} AS """.format(*tup)
        select = """(SELECT {0}.event AS {0}, {1}.event as {1} FROM {0},{1}""".format(*tup)
        where = """ WHERE ST_DWithin({0}.location,{1}.location,{2},true))""".format(tup[0],tup[1],h)
        query = create+select+where
        cursor.execute(query)
        conn.commit()
        query = """SELECT * FROM {0}{1}""".format(*tup)
        cursor.execute(query)
        results = cursor.fetchall()
        name = ""
        for p in tup:
            name += str(p[0])
        table[name] = results
        query = """SELECT ST_X(S.geo1) AS X1,ST_Y(S.geo1) AS Y1,ST_X(S.geo2) AS X2,ST_Y(S.geo2) AS Y2 
                FROM (SELECT ST_Transform(e.{0}::geometry,4326) as geo1,ST_Transform(e.{1}::geometry,4326) as geo2
		        FROM (SELECT {0}.location AS {0}, {1}.location as {1} FROM {0},{1} 
	  			WHERE ST_DWithin({0}.location,{1}.location,{2},true)) as e) as S""".format(*tup,h)
        cursor.execute(query)
        linePoints.extend(cursor.fetchall())
    return table,linePoints

def relationalJoin(h,name,columns):
    table = {}
    create="""CREATE TABLE {0} AS """.format(name)
    select = """(SELECT * FROM {0} NATURAL JOIN {1} NATURAL JOIN {2})""".format(*columns)
    query = create+select
    cursor.execute(query)
    conn.commit()
    query = """SELECT {0} FROM {1}""".format(",".join([*name]),name)
    cursor.execute(query)
    results = cursor.fetchall()
    return results

def generateInstanceTable(h,size,keys,exclude=[]):
    nextTable = {}
    for comb in sorted(combinations(keys, 2)):
        key = set([*comb[0]]+[*comb[1]])
        col = set([*comb[0]]).intersection([*comb[1]])
        col = "".join(sorted(key - col))
        if(len(key) > size):
            continue
        if(exclude != []):
            flag = False
            for excl in exclude:
                if excl.issubset(key):
                    flag = True
                    break
            if flag:
                continue
        key = ''.join(sorted(key))
        nextTable[key] = list(comb) + [col]
    table = {}
    for key,value in nextTable.items():
        rjoin = relationalJoin(h,key,sorted(value))
        table[key] = rjoin
    return table

def getStudyRegion():
    query = """SELECT max(T.long) as maxlong, max(T.lat) as maxlat, min(T.long) as minlong, min(T.lat) as minlat 
    FROM (SELECT ST_X (S.geo) AS long,ST_Y (S.geo) AS lat 
    FROM (SELECT ST_Transform (events.location::geometry,4326) as geo FROM events) as S) as T"""
    cursor.execute(query)
    return cursor.fetchall()[0]

def getRectangleArea(Rect):
    query="""SELECT ST_AREA(ST_MAKEENVELOPE({2},{3},{0},{1},4326))""".format(*Rect)
    cursor.execute(query)
    return cursor.fetchall()[0][0]

def makeClusters(eps,minpoints):
    query="""SELECT max(T.long) as maxlong, max(T.lat) as maxlat, min(T.long) as minlong, min(T.lat) as minlat 
    FROM (SELECT ST_X (S.geo) AS long,ST_Y (S.geo) AS lat,cid
    FROM (SELECT event,location::geometry as geo ,ST_ClusterDBSCAN(ST_Transform(location::geometry,5243),{0},{1}) OVER () as cid
    FROM events) as S) as T GROUP BY cid
    """.format(eps,minpoints)
    cursor.execute(query)
    return cursor.fetchall()