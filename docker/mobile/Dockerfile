FROM cirrusci/flutter:3.16.0 AS builder

WORKDIR /app

COPY mobile/ .

RUN flutter pub get && \
    flutter clean && \
    flutter build apk --release --split-per-abi && \
    flutter build ios --release --no-codesign || true

FROM alpine:3.19 AS runner

RUN apk add --no-cache bash

RUN mkdir -p /app/build

COPY --from=builder /app/build/app/outputs/flutter-apk/ /app/build/apk/
COPY --from=builder /app/build/ios/ /app/build/ios/

RUN ls -la /app/build/apk/ && \
    ls -la /app/build/ios/ || true

VOLUME ["/app/build"]

CMD ["cp", "-r", "/app/build/.", "/output/"]
