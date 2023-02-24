#!/bin/bash
sudo yum update -y
sudo yum -y install tomcat tomcat-admin-webapps
sudo systemctl start tomcat.service
sudo systemctl enable tomcat.service
sudo mkdir /usr/share/tomcat/webapps/ROOT
echo FPT Wellcome $(hostname -f) | sudo tee -a /usr/share/tomcat/webapps/ROOT/index.html
sudo systemctl restart tomcat.service