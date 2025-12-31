export interface Branch {
  value: string; // works as key/id
  label: string; // Display name
  rep: string; // Representative
  address: string;
  phone: string;
}

export const BRANCHES: Branch[] = [
  {
    value: "FZ_MAIN",
    label: "福州分行营业部",
    rep: "张三",
    address: "福建省福州市鼓楼区五四路123号",
    phone: "0591-88888888"
  },
  {
    value: "FZ_GL",
    label: "福州鼓楼支行",
    rep: "李四",
    address: "福建省福州市鼓楼区八一七北路456号",
    phone: "0591-87654321"
  },
  {
    value: "FZ_TJ",
    label: "福州台江支行",
    rep: "王五",
    address: "福建省福州市台江区江滨中大道789号",
    phone: "0591-12345678"
  },
  {
    value: "XM_MAIN",
    label: "厦门分行营业部",
    rep: "赵六",
    address: "福建省厦门市思明区鹭江道100号",
    phone: "0592-22222222"
  }
];

export const ID_TYPES = [
  { label: '居民身份证', value: '居民身份证' },
  { label: '港澳台居民居住证', value: '港澳台居民居住证' },
  { label: '港澳居民来往内地通行证', value: '港澳居民来往内地通行证' },
  { label: '台湾居民来往大陆通行证', value: '台湾居民来往大陆通行证' },
  { label: '护照', value: '护照' },
  { label: '其他', value: '其他' },
];
