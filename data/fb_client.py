# import requests
# from django.conf import settings
#
#
# # TODO Refactor - Należy wyprowadzić klasę FacebookClient.
#
# def send_message(recipient_id, buttons):
#     url = f"https://graph.facebook.com/v18.0/me/messages?access_token={settings.FACEBOOK_ACCESS_TOKEN}"
#
#     if buttons:
#         payload = {
#             "recipient": {"id": recipient_id},
#             "message": {
#                 "attachment": {
#                     "type": "template",
#                     "payload": {
#                         "template_type": "button",
#                         "text": "Wybierz mecz, którego wynik chcesz zaktualizować:",
#                         "buttons": buttons
#                     }
#                 }
#             }
#         }
#     else:
#         payload = {
#             "recipient": {"id": recipient_id},
#             "message": {
#                 "text": "Nie ma meczów"
#             }
#         }
#
#     res = requests.post(url, json=payload)
