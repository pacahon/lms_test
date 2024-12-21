```bash
docker volume create --name lms-media
docker-compose down -v
docker-compose build nginx
docker-compose up -d nginx
```

### Debug container

```bash
docker exec -it <image> /bin/bash
docker run --rm -it --entrypoint=/bin/bash <image>
```
