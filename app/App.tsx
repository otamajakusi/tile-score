/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 * @flow
 */

import React, {Component} from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
  Platform,
  Dimensions,
  StyleSheet,
  ScrollView,
  Text,
  TouchableOpacity,
  Modal,
  View,
  PermissionsAndroid,
  StatusBar,
} from 'react-native';
import ImageEditor from '@react-native-community/image-editor';
import RNFS from 'react-native-fs';
import {RNCamera} from 'react-native-camera';
import {Table, Col, Rows} from 'react-native-table-component';
import {openInStore} from 'react-native-app-link';
import DeviceInfo from 'react-native-device-info';

import {Aes} from './wbaes';
import {MAGIC} from './magic';

const IMAGE_WIDTH = 512;
const IMAGE_HEIGHT = 512;
let SERVER_URL;
// v1 endpoint: 'https://tile-score.otamajakusi.net/v1/score';
if (__DEV__) {
  SERVER_URL = 'https://dev-tile-score.otamajakusi.net/v2/score';
  // SERVER_URL = 'http://192.168.0.101:3000/dev/v2/score';
} else {
  SERVER_URL = 'https://tile-score.otamajakusi.net/v2/score';
}

const FETCH_TIMEOUT_DEFAULT = 100000; // 10sec
const FETCH_TIMEOUT = 300000; // 30sec

const fetchWithTimeout = (url, options, timeout = FETCH_TIMEOUT_DEFAULT) => {
  return Promise.race([
    fetch(url, options),
    new Promise((_, reject) => setTimeout(() => reject(new Error('タイムアウト')), timeout)),
  ]);
};

const stringToHex = (str) => {
  var hex = '';
  for (var i = 0; i < str.length; i++) {
    hex += ('00' + str.charCodeAt(i).toString(16)).slice(-2);
  }
  return hex;
};

const genApiKey = () => {
  const options = {
    encoding: 'str',
  };
  const date = new Date();
  const epoc = Math.floor(date.getTime() / 1000);
  const plain = `${MAGIC}${epoc}`;
  const apikey = Aes.encrypt(plain, options);
  return stringToHex(apikey);
};

const log = (...args) => {
  if (__DEV__) {
    console.log(...args);
  }
};

const generateScoreDealer = (han, fu) => {
  // https://mj-dragon.com/calc/index-score.html
  switch (han) {
    case 0:
    case 1:
      switch (fu) {
        case 30:
          return '1500(500オール)';
        case 40:
          return '2000(700オール)';
        case 50:
          return '2400(800オール)';
        case 60:
          return '2900(1000オール)';
        case 70:
          return '3400(1200オール)';
        case 80:
          return '3900(1300オール)';
        case 90:
          return '4400(1500オール)';
        case 100:
          return '4800(1600オール)';
        default:
        case 110:
          return '5300(1800オール)';
      }
    case 2:
      switch (fu) {
        case 20:
          return '(700オール)';
        case 25:
          return '2400';
        case 30:
          return '2900(1000オール)';
        case 40:
          return '3900(1300オール)';
        case 50:
          return '4800(1600オール)';
        case 60:
          return '5800(2000オール)';
        case 70:
          return '6800(2300オール)';
        case 80:
          return '7700(2600オール)';
        case 90:
          return '8700(2900オール)';
        case 100:
          return '9600(3200オール)';
        default:
        case 110:
          return '10600(3600オール)';
      }
    case 3:
      switch (fu) {
        case 20:
          return '(1300オール)';
        case 25:
          return '4800(1600オール)';
        case 30:
          return '5800(2000オール)';
        case 40:
          return '7700(2600オール)';
        case 50:
          return '9600(3200オール)';
        case 60:
          return '11600(3900オール)';
        default:
          return '12000(4000オール)';
      }
    case 4:
      switch (fu) {
        case 20:
          return '(2600オール)';
        case 25:
          return '9600(3200オール)';
        case 30:
          return '11600(3900オール)';
        default:
          return '12000(4000オール)';
      }
    case 5:
      return '12000(4000オール)';
    case 6:
    case 7:
      return '18000(6000オール)';
    case 8:
    case 9:
    case 10:
      return '24000(8000オール)';
    case 11:
    case 12:
      return '36000(12000オール)';
  }
  if (han >= 13 && han <= 25) {
    return '48000(16000オール)';
  }
  if (han >= 26 && han <= 38) {
    return '96000(32000オール)';
  }
  if (han >= 39) {
    return '144000(48000オール)';
  }
  return null;
};

const generateScoreNondealer = (han, fu) => {
  // https://mj-dragon.com/calc/index-score.html
  switch (han) {
    case 0:
    case 1:
      switch (fu) {
        case 30:
          return '1000(300,500)';
        case 40:
          return '1300(400,700)';
        case 50:
          return '1600(400,800)';
        case 60:
          return '2000(500,1000)';
        case 70:
          return '2300(600,1200)';
        case 80:
          return '2600(700,1300)';
        case 90:
          return '2900(800,1500)';
        case 100:
          return '3200(800,1600)';
        default:
        case 110:
          return '3600(900,1800)';
      }
    case 2:
      switch (fu) {
        case 20:
          return '(400,700)';
        case 25:
          return '1600';
        case 30:
          return '2000(500,1000)';
        case 40:
          return '2600(700,1300)';
        case 50:
          return '3200(800,1600)';
        case 60:
          return '3900(1000,2000)';
        case 70:
          return '4500(1200,2300)';
        case 80:
          return '5200(1300,2600)';
        case 90:
          return '5800(1500,2900)';
        case 100:
          return '6400(1600,3200)';
        default:
        case 110:
          return '7100(1800,3600)';
      }
    case 3:
      switch (fu) {
        case 20:
          return '(700,1300)';
        case 25:
          return '3200(800,1600)';
        case 30:
          return '3900(1000,2000)';
        case 40:
          return '5200(1300,2600)';
        case 50:
          return '6400(1600,3200)';
        case 60:
          return '7700(2000,3900)';
        default:
          return '8000(2000,4000)';
      }
    case 4:
      switch (fu) {
        case 20:
          return '(1300,2600)';
        case 25:
          return '6400(1600,3200)';
        case 30:
          return '7700(2000,3900)';
        default:
          return '8000(2000,4000)';
      }
    case 5:
      return '8000(2000,4000)';
    case 6:
    case 7:
      return '12000(3000,6000)';
    case 8:
    case 9:
    case 10:
      return '16000(4000,8000)';
    case 11:
    case 12:
      return '24000(6000,12000)';
  }
  if (han >= 13 && han <= 25) {
    return '32000(8000,16000)';
  }
  if (han >= 26 && han <= 38) {
    return '64000(16000,32000)';
  }
  if (han >= 39) {
    return '96000(24000,48000)';
  }
  return null;
};

const labelJaTable = {
  m1: '萬子1',
  m2: '萬子2',
  m3: '萬子3',
  m4: '萬子4',
  m5: '萬子5',
  m6: '萬子6',
  m7: '萬子7',
  m8: '萬子8',
  m9: '萬子9',
  s1: '索子1',
  s2: '索子2',
  s3: '索子3',
  s4: '索子4',
  s5: '索子5',
  s6: '索子6',
  s7: '索子7',
  s8: '索子8',
  s9: '索子9',
  p1: '筒子1',
  p2: '筒子2',
  p3: '筒子3',
  p4: '筒子4',
  p5: '筒子5',
  p6: '筒子6',
  p7: '筒子7',
  p8: '筒子8',
  p9: '筒子9',
  ton: '東',
  nan: '南',
  sha: '西',
  pei: '北',
  haku: '白',
  hatsu: '發',
  chun: '中',
  back: '裏',
};

const labelJa = (label) => labelJaTable[label];

interface State {
  busy: boolean;
  imageUri: string | null;
  fetchError: string | null;
  fetchScore: string | null;
}

export default class App extends Component<{}> {
  taking = false;
  camera;
  state: State;

  constructor(props) {
    super(props);
    this.state = {
      busy: false,
      imageUri: null,
      fetchError: null,
      fetchScore: null,
    };
  }

  renderScoreTable(fu, _han) {
    let scoreData = [[], [], []];
    let hanList;
    const hanListBase = [
      [1],
      [2],
      [3],
      [4],
      [5],
      [6, 7],
      [8, 10],
      [11, 12],
      [13, 25],
      [26, 38],
      [39],
    ];
    if (fu === 20 || fu === 25) {
      hanList = hanListBase.slice(1);
    } else {
      hanList = hanListBase;
    }
    hanList.forEach((han, index) => {
      if (Math.max(...han) < _han) {
        return;
      }
      if (index + 1 === hanList.length) {
        // last index
        scoreData[0].push(`${han[0]}..ハン`);
      } else if (han.length === 1) {
        scoreData[0].push(`${han[0]}ハン`);
      } else {
        scoreData[0].push(`${han[0]}..${han[1]}ハン`);
      }
      scoreData[1].push(generateScoreDealer(han[0], fu).replace('(', '\n('));
      scoreData[2].push(generateScoreNondealer(han[0], fu).replace('(', '\n('));
    });
    const widthArr = scoreData[0].map((han) => 128);
    const heightArr = [52, 52, 52];
    const heightArrTot = heightArr.reduce((prev, curr) => prev + curr);
    return (
      <View style={{flex: 1, flexDirection: 'row'}}>
        <View style={{height: heightArrTot}}>
          <Table borderStyle={styles.scoreTableHeader}>
            <Col
              heightArr={heightArr}
              data={[`${fu}符`, '親', '子']}
              textStyle={styles.tableText}
            />
          </Table>
        </View>
        <View style={{height: heightArrTot}}>
          <ScrollView horizontal={true}>
            <Table borderStyle={styles.scoreTable}>
              <Rows
                heightArr={heightArr}
                widthArr={widthArr}
                style={{backgroundColor: 'rgba(255,255,102,0.4)'}}
                data={scoreData}
                textStyle={styles.tableText}
              />
            </Table>
          </ScrollView>
        </View>
      </View>
    );
  }

  renderCameraUpper() {
    const touchableOpacityView = (
      <View style={[styles.touchableContainer]}>
        <TouchableOpacity
          style={styles.touchable}
          onPress={() => {
            this.takePictureWithPermissions(false);
            log('ロン');
          }}>
          <Text style={styles.guideText}>ロン</Text>
        </TouchableOpacity>
      </View>
    );
    return (
      <View style={{flex: 1, flexDirection: 'row'}}>
        <View style={[styles.guideArea, styles.guideAreaOpen]}>
          <Text style={styles.guideText}>副露牌(暗槓は含まない)</Text>
        </View>
        <View style={[styles.guideArea, styles.guideAreaWin]}>
          <Text style={styles.guideText}>アガリ牌</Text>
        </View>
        {touchableOpacityView}
      </View>
    );
  }

  renderCamera() {
    return (
      <View style={styles.image}>
        <RNCamera
          captureAudio={false}
          ref={(cam) => {
            this.camera = cam;
          }}
          style={styles.preview}>
          {this.renderCameraUpper()}
          <View style={{flex: 1, flexDirection: 'row'}}>
            <View style={[styles.guideArea, styles.guideAreaClosed]}>
              <Text style={styles.guideText}>手の内(暗槓を含む)</Text>
            </View>
            <View style={styles.touchableContainer}>
              <TouchableOpacity
                style={styles.touchable}
                onPress={() => {
                  this.takePictureWithPermissions(true);
                  log('ツモ');
                }}>
                <Text style={styles.guideText}>ツモ</Text>
              </TouchableOpacity>
            </View>
          </View>
        </RNCamera>
      </View>
    );
  }

  renderScoreModal() {
    if (!(this.state.fetchError || this.state.fetchScore)) {
      return null;
    }

    let title: string;
    let scoreTable = null;
    if (this.state.fetchError) {
      title = `エラー: ${this.state.fetchError}`;
    } else if (this.state.fetchScore && this.state.fetchScore.error) {
      title = '認識失敗';
    } else {
      title = `${this.state.fetchScore.yaku} ${this.scoreString()}`;
      scoreTable = this.renderScoreTable(
        this.state.fetchScore.fu,
        this.state.fetchScore.han,
      );
    }
    return (
      <Modal
        animationType={'fade'}
        transparent={true}
        visible
        supportedOrientations={['landscape']}
        onRequestClose={() => {
          log('Modal has been closed.');
        }}>
        <View style={styles.modal}>
          <Text style={[styles.guideText, {fontSize: 24, fontWeight: '500'}]}>
            {title}
          </Text>
          {scoreTable}
          <TouchableOpacity
            style={[styles.guideArea, styles.closeButton]}
            onPress={() => {
              this.setState({
                fetchError: null,
                fetchScore: null,
                imageUri: null,
              });
            }}>
            <Text style={[styles.guideText, {fontWeight: '500'}]}>閉じる</Text>
          </TouchableOpacity>
        </View>
      </Modal>
    );
  }

  renderBoxes() {
    if (!this.state.fetchScore || !this.state.fetchScore.boxes) {
      return null;
    }
    const boxes = this.state.fetchScore.boxes;
    const width = this.state.fetchScore.width;
    const height = this.state.fetchScore.height;
    const barHeight = StatusBar.currentHeight || 0;
    const window = Dimensions.get('window');
    const ratio = window.width / width;
    const yoff = (height * ratio - (window.height - barHeight)) / 2
    const boxViews = boxes.map((box) => {
      const xmin = box[1] * ratio;
      const ymin = box[2] * ratio - yoff;
      const xmax = box[3] * ratio;
      const ymax = box[4] * ratio - yoff;
      return [
        <View
          key={`label${xmin}${ymin}`}
          style={{
            backgroundColor: 'mediumblue',
            position: 'absolute',
            left: xmin,
            top: ymin - 12,
            width: xmax - xmin,
            height: 12,
            flex: 1,
            alignItems: 'center',
          }}>
          <Text
            style={{
              marginLeft: 4,
              fontSize: 10,
              color: '#FFFFFF',
            }}>
            {labelJa(box[0])}
          </Text>
        </View>,
        <View
          key={`box${xmin}${ymin}`}
          style={{
            borderColor: 'mediumblue',
            borderWidth: 2,
            position: 'absolute',
            left: xmin,
            top: ymin,
            width: xmax - xmin,
            height: ymax - ymin,
            flex: 1,
            alignItems: 'center',
          }}
        />,
      ];
    });
    return boxViews;
  }

  renderImage() {
    return (
      <View style={styles.image}>
        {this.renderScoreModal()}
        <Image
          source={{uri: this.state.imageUri}}
          style={styles.image}
        />
      </View>
    );
  }

  render() {
    return (
      <View style={styles.container}>
        {this.state.imageUri ? this.renderImage() : this.renderCamera()}
        {this.state.busy && (
          <ActivityIndicator style={styles.loading} size="large" />
        )}
        {this.renderBoxes()}
      </View>
    );
  }

  grantPermissions = () => {
    if (Platform.OS === 'android') {
      const permissions = [
        //PermissionsAndroid.PERMISSIONS.CAMERA,
        PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
        PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
      ];
      return PermissionsAndroid.requestMultiple(permissions);
    } else {
      return Promise.resolve();
    }
  };

  takePictureWithPermissions = (tsumo) => {
    const promise = this.grantPermissions();
    promise.then((res) => this.takePicture(tsumo));
  };

  takePicture = (tsumo) => {
    if (this.camera && this.taking === false) {
      this.taking = true;
      this.setState({busy: true});
      let options = {width: 1024};
      if (Platform.OS === 'android') {
        options.orientation = 'landscapeLeft';
      }
      this.camera
        .takePictureAsync(options)
        .then((data) => {
          log('data', data);
          this.taking = false;
          const img = data;
          // tan,pin,sanshoku
          // const img = Image.resolveAssetSource(require('./screenshots/IMG_20181117_102332.jpg'));
          // yakuhai(hatsu)
          //const img = Image.resolveAssetSource(require('./screenshots/IMG_20181117_123236.jpg'));
          // daisangen
          //const img = Image.resolveAssetSource(require('./screenshots/IMG_20181117_103150.jpg'));
          const imgUri = img.uri;
          const imgWidth = img.width;
          const imgHeight = img.height;
          //log('img', img);
          ImageEditor.cropImage(imgUri, {
            offset: {x: 0, y: 0},
            size: {width: imgWidth, height: imgHeight},
            displaySize: {
              width: (IMAGE_WIDTH * imgWidth) / imgHeight,
              height: IMAGE_HEIGHT,
            },
          }).then(
            (res) => {
              Image.getSize(res, (width, height) =>
                log('resized', width, height),
              );
              this.setState({imageUri: res});
              this.postImage(res, tsumo);
            },
            (err) => {
              console.error('cropImage: ', err);
            },
          );
        })
        .catch((err) => console.error('takePicttureAsync: ', err));
    }
  };

  scoreString = () => {
    const score = this.state.fetchScore;
    return `[${score.fu}符 ${score.han}ハン]`;
  };

  alertNeedUpdate = () => {
    // https://itunes.apple.com/jp/app/id1443045253
    // https://play.google.com/store/apps/details?id=com.tile_score_app
    const storeConfig = {
      appName: null,
      appStoreId: '1443045253',
      appStoreLocale: 'jp',
      playStoreId: 'com.tile_score_app',
    };
    const onPress = () => {
      this.setState({fetchError: 'アプリの更新が必要です'});
      openInStore(storeConfig);
    };
    Alert.alert('確認', 'アプリの更新が必要です', [{text: 'OK', onPress}]);
  };

  postImage = (uri, tsumo) => {
    RNFS.readFile(uri, 'base64').then(
      async (res) => {
        log(`${SERVER_URL}`);
        try {
          const resp = await fetchWithTimeout(
            `${SERVER_URL}`,
            {
              method: 'POST',
              headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                image: res,
                tsumo: tsumo,
                apikey: genApiKey(),
                version: DeviceInfo.getVersion(),
                device: DeviceInfo.getDeviceName(),
              }),
            },
            FETCH_TIMEOUT,
          );
          log(resp);
          if (resp.ok) {
            const json = await resp.json();
            log('json', json);
            this.setState({fetchScore: json});
          } else if (resp.status === 403) {
            this.alertNeedUpdate();
          } else {
            log('errors', resp);
            this.setState({fetchError: `得点計算失敗(${resp.status})`});
          }
        } catch (err) {
          log('err', err);
          this.setState({fetchError: err.message});
        }
        this.setState({busy: false});
      },
      (err) => console.error('getBase64ForTag: ', err),
    );
  };
}

const MARGIN_HORIZONTAL = 16;
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  preview: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    height: Dimensions.get('window').height,
    width: Dimensions.get('window').width,
  },
  guideArea: {
    justifyContent: 'flex-end',
    alignItems: 'center',
    borderColor: '#FF6928',
    borderWidth: 1,
    borderRadius: 20,
    marginVertical: 12,
    marginHorizontal: MARGIN_HORIZONTAL,
  },
  guideAreaOpen: {
    flex: 8,
    height: Dimensions.get('window').height / 2 - 24 - 6,
  },
  guideAreaWin: {
    flex: 2,
    marginLeft: 0,
    height: Dimensions.get('window').height / 2 - 24 - 6,
  },
  guideAreaClosed: {
    flex: 1,
    height: Dimensions.get('window').height / 2 - 24 - 6,
    width: Dimensions.get('window').width - MARGIN_HORIZONTAL * 2,
  },
  guideText: {
    fontSize: 16,
    color: '#FFFFFF',
    textShadowColor: 'rgba(255, 106, 40, 0.75)',
    textShadowOffset: {width: -1, height: 1},
    textShadowRadius: 10,
  },
  image: {
    height: '100%',
    width: '100%',
  },
  loading: {
    flex: 1,
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255,255,255,0)',
  },
  modal: {
    flex: 1,
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0)',
    paddingTop: 32,
    paddingHorizontal: 32,
  },
  closeButton: {
    justifyContent: 'center',
    alignItems: 'center',
    borderColor: '#FFFF66',
    borderWidth: 4,
    borderRadius: 12,
    height: 42,
    width: 114,
  },
  touchableContainer: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    width: '100%',
    height: '100%',
    alignItems: 'flex-start',
    justifyContent: 'center',
  },
  touchable: {
    width: '20%',
    height: '60%',
    alignItems: 'center',
    justifyContent: 'flex-end',
    borderColor: '#FFFF66',
    borderWidth: 4,
    borderRadius: 32,
    marginLeft: 32,
    marginBottom: 8,
  },
  scoreTableHeader: {
    borderColor: 'transparent',
    borderWidth: 0,
  },
  scoreTable: {
    borderColor: '#FF6928',
    borderWidth: 1,
  },
  tableText: {
    fontSize: 18,
    color: '#FFFFFF',
    textShadowColor: 'rgba(255, 106, 40, 0.75)',
    textShadowOffset: {width: -1, height: 1},
    textShadowRadius: 10,
    textAlign: 'center',
  },
});
