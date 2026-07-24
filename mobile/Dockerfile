FROM cirrusci/flutter:3.13.9 AS builder

WORKDIR /app

COPY pubspec.yaml pubspec.lock* ./
RUN flutter pub get

COPY . .

RUN flutter clean && \
    flutter pub get && \
    flutter build apk --release

FROM alpine:3.18 AS runner

RUN apk add --no-cache bash

WORKDIR /app

COPY --from=builder /app/build/app/outputs/flutter-apk/app-release.apk /app/app-release.apk
COPY --from=builder /app/build/app/outputs/bundle/release/app-release.aab /app/app-release.aab

RUN echo "Build complete. APK and AAB files are available in /app/"

CMD ["/bin/sh", "-c", "echo 'SecureBank Flutter Build' && ls -la /app/"]
