<script setup>

import Nav from "@/components/Nav.vue";
import {RouterView} from "vue-router";
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
