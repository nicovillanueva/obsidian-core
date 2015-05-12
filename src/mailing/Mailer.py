import logging
from ..CustomUtils import get_random_str

class Mailer():
    """Send reports of collected screenshots"""
    def __init__(self, host, port, user=None, passwd=None, tls=False, ehlo=False):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.tls = tls
        self.ehlo = ehlo

        self.logger = logging.getLogger('obs.Mailer')

    def send_report(self, recipients, params, imagewidth=800):
        import smtplib, uuid
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.image import MIMEImage
        from email.header import Header
        import socket

        me = "obsidian@viajeros.com"
        you = recipients

        msg = MIMEMultipart('related')
        msg['Subject'] = Header(u"Obsidian report for " + params["test_start"], 'utf-8')
        msg['From'] = me
        msg['To'] = ", ".join(recipients) if len(recipients) > 1 else recipients[0]

        # Hierarchy to be GMail compliant
        msg_alt = MIMEMultipart('alternative')
        msg.attach(msg_alt)

        # Text-only version for archaic or retarded mail clients. Also required by Gmail.
        msg_text = MIMEText(u'Text-only image report wouldn\'t make much sense, now would it?')
        msg_alt.attach(msg_text)

        # E-Mail header
        strhtml = '<div dir="ltr">'
        with open('src/mailing/MailerStyle.css') as style: strhtml += style.read()
        strhtml += '<span id="header">Bonjour!</span><br><br><span>At ' + params["test_start"] + ', I saw this thingies:</span><br>'

        temp_files = []
        # Each image with it's information
        for each in params["screenshots"]:
            path = each.path
            fn = path[path.rfind("/")+1::]
            uid = str(uuid.uuid4())
            strhtml += '<br><hr><br>'
            strhtml += '<span class="category">Browser: </span><span class="detail">' + each.browser + '</span><br>'
            strhtml += '<span class="category">URL: </span><span class="detail">' + each.url + '</span><br>'
            strhtml += '<span class="category">Date: </span><span class="detail">' + each.date_taken + '</span><br>'
            strhtml += '<span class="category">Filename: </span><span class="detail">' + each.path + '</span><br>'
            strhtml += '<img src="cid:' + uid + '" alt="' + each.path + '"><br>'

            # Resize image if it's too large
            new_path = self._resize_image(path, imagewidth)
            self.logger.info("Created temporary screenshot file: %s" % new_path)
            temp_files.append(new_path)

            # Attach the image file
            with open(new_path, 'rb') as thefile:
                msg_image = MIMEImage(thefile.read(), name=fn)
                msg.attach(msg_image)
            msg_image.add_header('Content-ID', uid)
            msg_image.add_header('Content-Disposition', fn)

        msg_html = MIMEText(unicode(strhtml), 'html', 'utf-8')
        msg_alt.attach(msg_html)

        # ---------------------------------

        self.logger.debug("Building SMTP lib stuff")
        try:
            s = smtplib.SMTP()
            if type(self.port) is int:
                self.logger.debug("Will build SMTP using: " + str(self.host) + ":" + str(self.port))    
            else:
                self.logger.debug("Will build SMTP using: " + str(self.host) + ":25")
                self.port = 25

            s = smtplib.SMTP(self.host, self.port, socket.getfqdn(), 10)
            self.logger.debug("Built SMTP.")
            
            if self.tls: s.starttls() ; self.logger.debug("Built with TLS")
            if self.ehlo: s.ehlo() ; self.logger.debug("Built with EHLO")

            if self.user is not None and self.user != "":
                self.logger.debug("Logging with " + self.user + ":" + self.passwd)
                s.login(self.user, self.passwd)

            self.logger.info("Sending mail")
            s.sendmail(me, you, msg.as_string())
        except Exception, e:
            self.logger.error("Error when sending mail!!!")
            self.logger.error("Exception:" + str(e))
        finally:
            #for each in temp_files:
            #    remove(each)
            self.logger.info("Deleting temp files: " + str(temp_files))
            from os import remove
            map(remove, temp_files)
            s.quit()

    def _resize_image(self, imgpath, targetwidth=800):
        """
        Get a path, open as image, and resize if necessary. Overwrites the image
        Resizes to 800px width (overridable)
        """
        from PIL import Image
        img = Image.open(imgpath)
        if img.size[0] > targetwidth:
            targetperc = (targetwidth * 100) / img.size[0]
            self.logger.debug("Target percentage: " + str(targetperc) + "%")
            targetheight = (targetperc * img.size[1]) / 100
            self.logger.debug("Target size: " + str(targetwidth) + ":" + str(targetheight))

            new_img_path = str(get_random_str(amount=16)) + ".png"
            img.resize((targetwidth, targetheight), Image.ANTIALIAS).save(new_img_path)
        return new_img_path