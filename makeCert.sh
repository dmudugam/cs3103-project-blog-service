openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
  -subj "/C=CA/ST=New Brunswick/L=Fredericton/O=UNB/OU=CS/CN=cs3103.cs.unb.ca" \
  -addext "subjectAltName=DNS:cs3103.cs.unb.ca"


  chmod -R 755 .

  pip install -r requirements.txt