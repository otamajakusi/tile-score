## how this directory created
```
npx react-native init app --template react-native-template-typescript
```

## run app
start server (Metro server)
```
npx react-native start
```

and launch app from another terminal.
```
npx react-native run-android
```

## watchman error
[react-native start error]
https://github.com/facebook/react-native/issues/3199#issuecomment-145426578
```
echo 256 | sudo tee -a /proc/sys/fs/inotify/max_user_instances
echo 32768 | sudo tee -a /proc/sys/fs/inotify/max_queued_events
echo 65536 | sudo tee -a /proc/sys/fs/inotify/max_user_watches
watchman shutdown-server
```

[react-native-camera error]
https://github.com/react-native-community/react-native-camera/issues/2138#issuecomment-471669956
```
android {
  ...
  defaultConfig {
    ...
    missingDimensionStrategy 'react-native-camera', 'general' <-- insert this line
  }
}
```
