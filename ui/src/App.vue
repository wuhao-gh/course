<script setup>
import { RouterView } from 'vue-router'
import Nav from './components/Nav.vue'
</script>

<template>

  <div>
    <el-container>
      <el-header>
        <Nav />
      </el-header>

      <el-main>
        <RouterView />
      </el-main>
    </el-container>
  </div>

</template>

<style scoped>

</style>
