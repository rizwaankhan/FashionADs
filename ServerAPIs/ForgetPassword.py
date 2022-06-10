import json
import os
import secrets
import sys

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ServerAPIs.SendEmail import send_mail
from ServerAPIs.models import *


@api_view(['GET', 'POST'])
def reset_password(request):
    userJson = json.loads(json.dumps(request.data))
    try:
        user = Users.objects.get(email=userJson['email'])
    except Exception as e:
        context = {"data": {}, 'Status': False, 'Message': 'Invalid Email..!'}
        ShowException(e)
        return Response(context)
    if user and request.method == 'POST':
        user = Users.objects.get(id=user.id)
        token = secrets.token_hex(16)
        user.reset_token = token
        user.save()
        context = {"data": {'email': user.email},
                   'Message': 'your password reset Link Send to your Email',
                   'Status': True}
        try:
            reset_passwordHtml = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
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
                                        style="padding:16px 10px; line-height:24px; color:#0a0a0a; font-weight:bold"> Hi """ + user.first_name + """
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
    
    
                            You have requested password reset. To set a new password please click on Reset Password link
                            given below. This link will expire in 24 Hours.<br/>
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
                                        <a href=""" + userJson['url'] + token + """
                                           style="background-color:#000000; color:#ffffff; padding:6px 20px; font-size:14px; font-family:Arial, Helvetica, sans-serif; text-decoration:none; display:inline-block; text-transform:uppercase; margin-top:10px;">Reset
                                            Password</a></td>
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
    </html>"""

            send_mail(html=reset_passwordHtml, text='', subject='Password reset Token',
                      from_email='',
                      to_emails=[userJson['email']])
        except:
            return Response(context)
        return Response(context)


def ShowException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    print(e)
