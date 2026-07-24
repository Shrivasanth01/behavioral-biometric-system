FROM nginx:1.25-alpine

RUN apk add --no-cache \
    apache2-utils \
    curl \
    openssl

RUN mkdir -p /etc/nginx/ssl && \
    mkdir -p /var/log/nginx && \
    mkdir -p /var/cache/nginx && \
    touch /etc/nginx/htpasswd

RUN addgroup -g 1001 -S nginx && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

COPY nginx.conf /etc/nginx/nginx.conf

RUN chown -R nginx:nginx /var/log/nginx /var/cache/nginx /etc/nginx

EXPOSE 80 443

STOPSIGNAL SIGQUIT

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD nginx -t || exit 1

CMD ["nginx", "-g", "daemon off;"]
