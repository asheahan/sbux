
import json
import pika
import psycopg2 as pg
import time

# Load db configuration from file
with open('./config.json') as config_file:
    DB_CONFIG = json.load(config_file)["postgres"]

# setup queue
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='twitter',
                         type='fanout')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='twitter',
                   queue=queue_name)

# db connection
try:
    connection_string = "host='%s' dbname='%s' user='%s' password='%s'" % (DB_CONFIG['host'], DB_CONFIG['db'], DB_CONFIG['user'], DB_CONFIG['password'])

    print("Connecting to database\n ->%s" % connection_string)
    conn = pg.connect(connection_string)
    conn.autocommit = True
    # conn = pg.connect("dbname='" + DB_CONFIG.db +
    #                   "' user='" + DB_CONFIG.user +
    #                   "' host='" + DB_CONFIG.host +
    #                   "' password='" + DB_CONFIG.password + "'")
    print("Connected to database...")
    cur = conn.cursor()
except:
    print("Error connecting to database")
    exit()

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(' [x] %r' % body)
    data = json.loads(body.decode(encoding='utf-8'))
    cur.execute("INSERT INTO tweets (message, created_at, geo, src) VALUES (%s, %s, %s, %s);", (data['text'], time.ctime(data['created_at']), json.dumps(data['geo']), data['source'],))

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()