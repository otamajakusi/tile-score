# setup
```
npm i
(see ../env/README)
bash magicgen.sh
bash wbaesgen.sh
```

# start server
```
npx react-native start
```

# run app
```
npx react-native run-android
```

# run app with release
```
npx react-native run-android --variant=release
```
`android/app/build/outputs/apk/release/app-release.apk` is generated.

# generate Android App Bundle (aab)
```
cd android
./gradlew bundleRelease
```
`app/build/outputs/bundle/release/app-release.aab` is generated.

# error
https://github.com/facebook/react-native/issues/3199#issuecomment-145426578
```
echo 256 | sudo tee -a /proc/sys/fs/inotify/max_user_instances
echo 32768 | sudo tee -a /proc/sys/fs/inotify/max_queued_events
echo 65536 | sudo tee -a /proc/sys/fs/inotify/max_user_watches
watchman shutdown-server
```

# memo (how this directory was created)
```
npx react-native init app --template react-native-template-typescript
cd app
npm install react-native-fs --save --legacy-peer-deps
npx react-native link react-native-fs
npm install @react-native-community/image-editor --save --legacy-peer-deps
...
```

`android/app/build.gradle`
```
android {
  ...
  defaultConfig {
    ...
    missingDimensionStrategy 'react-native-camera', 'general' <-- insert this line
  }
}
```
