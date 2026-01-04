<template>
  <div id="app">
    <IoVMap />
  </div>
</template>

<script>
import IoVMap from './components/IoVMap.vue';

export default {
  name: 'App',
  components: {
    IoVMap
  }
}
</script>

<style>
/* 全局样式重置 */
body, html {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background-color: #021019; /* 防止加载时出现白边 */
  overflow: hidden; /* 禁止浏览器滚动条 */
}
#app {
  width: 100%;
  height: 100%;
}
</style>