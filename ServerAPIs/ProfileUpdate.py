import json
import os
import sys

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.SendEmail import send_mail
from ServerAPIs.models import *


@api_view(['POST'])
@csrf_exempt
def profile_update(request):
    userJson = json.loads(json.dumps(request.data))
    try:
        existingUser = userJson.get('update_id')
        user = Users.objects.get(id=existingUser)
    except Exception as e:
        context = {'Message': 'Error getting Users Data or User Not Exist', 'Status': False}
        ShowException(e)
        return Response(context)
    try:
        if user:
            user.first_name = userJson["first_name"]
            user.last_name = userJson["last_name"]
            user.gender = userJson["gender"]
            user.state = userJson["state"]
            user.city = userJson["city"]
            user.zip_code = userJson["zip_code"]
            user.street_address = userJson["street_address"]
            user.save()
            context = {"data": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "state": user.state,
                "city": user.city,
                "zip_code": user.zip_code,
                "street_address": user.street_address,
                "gender": user.gender,
                "latitude": user.latitude,
                "longitude": user.longitude,
            },
                "Status": True,
                "Message": 'Profile Updated Successfully...!',
            }
            try:
                AccountUpdateHtml = """
                            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
                            <html xmlns="http://www.w3.org/1999/xhtml">
                            <head>
                                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>Dresses Ads - Ads Network</title>
                                <style type="text/css">
                                    @media only screen and (max-width: 600px) {
                                        table[class="contenttable"] {
                                            width: 320px !important;
                                            border-width: 3px !important;
                                        }

                                        table[class="tablefull"] {
                                            width: 100% !important;
                                        }

                                        table[class="tablefull"] + table[class="tablefull"] td {
                                            padding-top: 0px !important;
                                        }

                                        table td[class="tablepadding"] {
                                            padding: 15px !important;
                                        }
                                    }
                                </style>
                            </head>

                <body style="margin:0; border: none; background:#f5f5f5">
                <table align="center" border="0" cellpadding="0" cellspacing="0" height="100%" width="100%">
                    <tr>
                        <td align="center" valign="top">
                            <table class="contenttable" border="0" cellpadding="0" cellspacing="0" width="600" bgcolor="#ffffff"
                                   style="border-width: 8px; border-style: solid; border-collapse: separate; border-color:#ececec; margin-top:40px; font-family:Arial, Helvetica, sans-serif">
                                <tr>
                                    <td>
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tbody>
                                            <tr>
                                                <td width="100%" height="40">&nbsp;</td>
                                            </tr>
                                            <tr>
                                                <td valign="top" align="center"><h2
                                                        style="font-size: 30px ; font-family: 'Waterfall', cursive ; text-align: center">
                                                    Dress </h2>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td width="100%" height="40">&nbsp;</td>
                                            </tr>
                                            <tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tbody>
                                            <tr>
                                                <td align="center"
                                                    style="padding:16px 10px; line-height:24px; color:#0a0a0a; font-weight:bold"> Hi """ + \
                                    user.first_name + """
                                                    <br>
                                                </td>
                                            </tr>
                                            <tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td class="tablepadding" style="padding:20px; font-size:14px; line-height:20px;">
                                        You have successfully updated your account on Dress Ads, click on the Account link to get
                                        started.<br/>
                                        </p>

                                    </td>
                                </tr>

                                <tr>
                                    <td>
                                        <table width="100%" cellspacing="0" cellpadding="0" border="0"
                                               style="font-size:13px;color:#555555; font-family:Arial, Helvetica, sans-serif;">
                                            <tbody>
                                            <tr>
                                                <td class="tablepadding" align="center"
                                                    style="font-size:14px; line-height:22px; padding:20px; border-top:1px solid #ececec;">
                                                    <a href="#"
                                                       style="background-color:#000000; color:#ffffff; padding:6px 20px; font-size:14px; font-family:Arial, Helvetica, sans-serif; text-decoration:none; display:inline-block; text-transform:uppercase; margin-top:10px;">My
                                                        Account</a></td>
                                            </tr>
                                            <tr></tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>

                                <tr>
                                    <td bgcolor="#fcfcfc" class="tablepadding"
                                        style="padding:20px 0; border-top-width:1px;border-top-style:solid;border-top-color:#ececec;border-collapse:collapse">
                                        <table width="100%" cellspacing="0" cellpadding="0" border="0"
                                               style="font-size:13px;color:#999999; font-family:Arial, Helvetica, sans-serif">
                                            <tbody>
                                            <tr>
                                                <td align="center" class="tablepadding" style="line-height:20px; padding:20px;">Dresses
                                                    Ads, <a href="mailto:info@adsnetwork.com">info@adsnetwork.com</a></td>
                                            </tr>
                                            <tr></tr>
                                            </tbody>
                                        </table>
                                        <table align="center">
                                            <tr>
                                                <td style="padding-right:10px; padding-bottom:9px;"><a href="#" target="_blank"
                                                                                                       style="text-decoration:none; outline:none;"><img
                                                        src="facebook.png" width="32" height="32" alt=""></a></td>
                                                <td style="padding-right:10px; padding-bottom:9px;"><a href="#" target="_blank"
                                                                                                       style="text-decoration:none; outline:none;"><img
                                                        src="twitter.png" width="32" height="32" alt=""></a></td>
                                                <td style="padding-right:10px; padding-bottom:9px;"><a href="#" target="_blank"
                                                                                                       style="text-decoration:none; outline:none;"><img
                                                        src="google_plus.png" width="32" height="32" alt=""></a></td>
                                                <td style="padding-right:10px; padding-bottom:9px;"><a href="#" target="_blank"
                                                                                                       style="text-decoration:none; outline:none;"><img
                                                        src="pinterest.png" width="32" height="32" alt=""></a></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <table width="100%" cellspacing="0" cellpadding="0" border="0"
                                   style="font-size:13px;color:#999999; font-family:Arial, Helvetica, sans-serif">
                                <tbody>
                                <tr>
                                    <td class="tablepadding" align="center" style="line-height:20px; padding:20px;"> 2021 Dress Ads All
                                        Rights Reserved.
                                    </td>
                                </tr>
                                <tr></tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                </table>
                </body>
                </html>
                            """
                send_mail(html=AccountUpdateHtml, text='', subject='Profile Update Confirmation',
                          from_email='',
                          to_emails=[user.email])
                return Response(context)
            except:
                return Response(context)
    except Exception as e:
        context = {'Message': 'Error While Saving Users Data..!', 'Status': False}
        ShowException(e)
        return Response(context)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
