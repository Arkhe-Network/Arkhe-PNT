FROM golang:1.22-alpine as builder

WORKDIR /app
COPY arkhe-hardware/qhttp-h/main.go .

RUN go mod init qhttp-h && go build -o qhttp-h main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
COPY --from=builder /app/qhttp-h /usr/local/bin/qhttp-h

CMD ["qhttp-h"]
