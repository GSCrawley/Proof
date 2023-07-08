import React from 'react';
import {View} from 'react-native';
import {Title} from 'react-native-paper';
// import base from './styles/base';

interface IMyFriendsProps {}

const MyFriends: React.FunctionComponent<IMyFriendsProps> = (props) => {
  return (
    <View style={base.centered}>
      <Title>MyFriends</Title>
    </View>
  );
};
export default MyFriends;