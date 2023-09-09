import psycopg2

conn = psycopg2.connect(database="spatialprojectdb",
                        host="localhost",
                        user="saksham",
                        password="saksham",
                        port="5432")
cursor = conn.cursor()