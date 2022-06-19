#!/usr/bin/env python3

import zulip
from pprint import pprint
from datetime import datetime
import html_text

from_ts = datetime.timestamp(datetime(2022, 5, 19))
to_ts = datetime.timestamp(datetime(2022, 6, 20))


# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="~/.zuliprc")

# Get the 1000 last messages from public streams
request = {
    "anchor": "newest",
    "num_before": 100,
    "num_after": 0,
    # "apply_markdown": False,
    "narrow": [
        {"operator": "streams", "operand": "public"},
    ],
}
result = client.get_messages(request)
if result['result'] != 'success':
    pprint(result)

messages = result['messages']

# Get the next bulk while starting date
while messages[0]['timestamp'] >= from_ts:
    request['anchor'] = messages[0]['id'] - 1
    result = client.get_messages(request)
    if result['result'] != 'success':
        pprint(result)
    if len(result['messages']) == 0:
        break
    messages = result['messages'] + messages

# Filter by date
messages = list(filter(
    lambda mes:  mes['timestamp'] >= from_ts and mes['timestamp'] < to_ts, messages))

# Sort by stream and topic
archive = {}

for mes in messages:
    stream_id = mes['display_recipient']
    subject = mes['subject']
    if not archive.get(stream_id):
        archive[stream_id] = {}
    if not archive[stream_id].get(subject):
        archive[stream_id][subject] = []

    archive[stream_id][subject].append(mes)


html = ""
index = []
stream_index = []
tid = 0

for stream_name, stream in archive.items():
    tid = tid + 1
    html = f'{html}</br></br><h2><b>Канал:</b> <a id="tid_{tid}">{stream_name}</a></h2>'
    stream_index = []
    index.append(
        (f'<li><a href="#tid_{tid}">{stream_name}</a></li>', stream_index))
    for topic_name, msg_list in stream.items():
        tid = tid + 1
        html = f'{html}</br><h3><i>{stream_name} ></i> <a id="tid_{tid}">{topic_name}</a></h3>'
        stream_index.append(f'<li><a href="#tid_{tid}">{topic_name}</a></li>')
        for mes in msg_list:
            html = (f"{html}"
                    f"<p><b>{datetime.fromtimestamp(mes['timestamp']).strftime('%d %b %Y %H:%M')}: {mes['sender_full_name']}:</b></p>"
                    f"{mes['content']}")


index_html = ''
for idx in index:
    index_html = f"{index_html}{idx[0]}<ul>{''.join(idx[1])}</ul>"


from_ts_str = datetime.fromtimestamp(from_ts).strftime('%d %b %Y')
to_ts_str = datetime.fromtimestamp(to_ts).strftime('%d %b %Y')

html = (f"<h1>Архив чата с {from_ts_str} до {to_ts_str}</h1>"
        f'<ul>{index_html}</ul> {html}')

from_ts_str = datetime.fromtimestamp(from_ts).strftime('%Y-%m-%d')
to_ts_str = datetime.fromtimestamp(to_ts).strftime('%Y-%m-%d')


html_file = open(f"./nsg_chat_archive_{from_ts_str}_{to_ts_str}.html", "w")
html_file.write(html)
html_file.close()


text = html_text.extract_text(html)
text_file = open(f"./nsg_chat_archive_{from_ts_str}_{to_ts_str}.txt", "w")
text_file.write(text)
text_file.close()
