import json
from enum import Enum
import re

import requests
from bs4 import BeautifulSoup

host_name = "alcasar-0320002d.smile-education.fr"

class ConnectionResults(Enum):
    """Enumeration used for connection result"""
    CONNECTION_SUCCESS = 0
    ALREADY_CONNECTED = 1
    PACKET_ERROR = 2
    BAD_PASSWORD = 3
    CANT_DETECT_PORTAL = 4


class DisconnectResult(Enum):
    """Enumeration used for disconnection result"""
    DISCONNECT_SUCCESS = 0
    NO_LOGOUT_LINK_AVAILABLE = 1
    PACKET_ERROR = 2

class Alcasar:
    """Class used to manage the connection with the Alcasar service."""
    def __init__(self):
        self.connection_statut = False
        self.logout_url = ""
        self.ses = requests.Session()
        self.ses.headers = {"Origin": host_name,
                            "Accept-Encoding": "gzip, deflate, br",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                            "Sec-Fetch-Mode": "navigate", "Connection": "keep-alive",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/126.0",
                            "Content-Type": "application/x-www-form-urlencoded", "Sec-Fetch-Site": "same-origin",
                            "Sec-Fetch-Dest": "document", "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
                            "Sec-Fetch-User": "?1"}

    def connect(self, username, password):
        """Send username and password to the Alcasar authentication service."""

        # Return if already connected
        self.update_statut()
        if self.connection_statut:
            return ConnectionResults.ALREADY_CONNECTED

        # Access the detection portal to be redirected to the authentication page.

        try:
            detect_portal_page = self.ses.get("http://detectportal.firefox.com/canonical.html", allow_redirects=False)
        except requests.exceptions.RequestException:
            return ConnectionResults.CANT_DETECT_PORTAL
        
        # Go to the captive portal page
        try:
            connection_page = self.ses.get(detect_portal_page.headers["Location"])
        except requests.exceptions.RequestException:
            return ConnectionResults.CANT_DETECT_PORTAL
        
        # Update the alcasar hostname
        re.match(r"https?:\/\/(([a-z,A-Z,0-9,\-,_]*\.)?[a-z,A-Z,0-9,\-,_]+\.[a-z]+)", connection_page.url).groups()[0]

        # We need a "challenge" value stored in a hidden input in the authentication
        # page to be sent to the post request
        soup = BeautifulSoup(connection_page.text, features="html.parser")
        input_challenge = soup.find("input", {"name": "challenge"})
        if input_challenge is None:
            return ConnectionResults.CANT_DETECT_PORTAL
        challenge = input_challenge["value"]

        # Send a post packet with username, password and challenge value to recover the redirection link
        data = f"challenge={challenge}&userurl=http%3A%2F%2Fdetectportal.firefox.com%2Fcanonical.html&username={username}&password={password}&button=Authentification"
        try:
            resp = self.ses.post(f"{host_name}/intercept.php",
                                 data=data,
                                 allow_redirects=False,
                                 headers={"Origin": host_name,
                                          "Referer": connection_page.url})
        except requests.exceptions.RequestException:
            return ConnectionResults.PACKET_ERROR

        # Send a get packet to connect to the account
        success = self.ses.get(resp.headers["Location"], allow_redirects=False)
        if success.headers["Location"].startswith(f"{host_name}/intercept.php?res=failed"):
            return ConnectionResults.BAD_PASSWORD

        return ConnectionResults.CONNECTION_SUCCESS

    def detect(self):
        """Return True if the current WI-FI network is managed by Alcasar."""
        try:
            ping_result = self.ses.get(host_name).status_code
            return ping_result == 200
        except requests.exceptions.RequestException:
            return False

    def update_statut(self):
        """Update the connexion statut"""
        try:
            data = self.ses.get(f"{host_name}:3990/json/status?callback=chilliJSON.reply", timeout=4)
            statut = json.loads(
                data.text[17:-1])
        except requests.exceptions.RequestException:
            self.connection_statut = False
            return False, ""

        # Update statuts variables with new data
        self.connection_statut = bool(statut["clientState"])
        self.logout_url = statut["redir"]["logoutURL"]
        return self.connection_statut, self.logout_url

    def disconnect(self):
        """Disconnect the user from the authentication service"""
        if self.logout_url:
            try:
                self.ses.get(self.logout_url)
                return DisconnectResult.DISCONNECT_SUCCESS
            except requests.exceptions.RequestException:
                return DisconnectResult.PACKET_ERROR
        return DisconnectResult.NO_LOGOUT_LINK_AVAILABLE


Alcasar().connect("", "")
