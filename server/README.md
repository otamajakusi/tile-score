yolov3-tile_900.weights: 022791ec3c78ee435d8ab93a4c0d6993c340b900 (sha1hash)

sls print # to debug serverless.yml

# setup
npm install

# debug local
launch offline server
```bash
$ npx sls offline --host 0.0.0.0
```

request to the local server
```bash
$ bash test.sh localhost:3000
```
