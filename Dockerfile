# Dockerfile для Nextcloud
FROM nextcloud:33.0.3-apache

COPY nas-init.sh /nas-init.sh
RUN chmod +x /nas-init.sh

ENTRYPOINT ["/nas-init.sh"]
CMD ["apache2-foreground"]
