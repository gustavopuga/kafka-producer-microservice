from kafka import KafkaProducer
from kafka.errors import KafkaError
from flask import make_response, abort
from datetime import datetime
import requests
import json, os

def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

def create(msg):
    try:
        texto = msg.get("texto", None)
        topico = os.environ['TOPICO']
        broker = os.environ['HOST'] + ":" + os.environ['PORTA']
        print(broker)

        producer = KafkaProducer(bootstrap_servers=[broker])

        # Asynchronous by default
        future = producer.send(topico, texto.encode('utf-8'))
        # Block for 'synchronous' sends
        record_metadata = future.get(timeout=10)
        
    except Exception as e:
        # Decide what to do if produce request failed...
        print(repr(e))
        abort(
            406,
            "Erro ao enviara msg pro Kafka: "+repr(e),
        )

    # Successful result returns assigned partition and offset
    print ('Sucesso no envio. Topico: '+str(record_metadata.topic)+' Particao :' + str(record_metadata.partition) + ' Offset: ' + str(record_metadata.offset))
    postMSG_criada_para_o_slack(texto)
    return make_response(
        "Mensagem criada: "+str(texto), 201
    )
    
def postMSG_criada_para_o_slack(msg):
    # format payload for slack
    sdata = formatForSlack(msg)
    url = 'https://hooks.slack.com/services/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'
    r = requests.post(url, sdata, headers={'Content-Type': 'application/json'}, verify=False)
    if r.status_code == 200:
      print('SUCCEDED: Sent slack webhook')
    else:
      print('FAILED: Send slack webhook')

def formatForSlack(msg):
  payload = {
    "channel":'#sync',
    "username":'gustavo_kafka_producer',
    "text": msg,
    "icon_emoji":':mailbox_with_mail:'
  }
  return json.dumps(payload)

