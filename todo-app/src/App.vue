<template>
  <div
    class="
      bg-gray-100
      min-h-screen
      flex
      justify-center
      items-start
      text-gray-900
    "
  >
    <div class="bg-white p-4 mt-8 rounded shadow">
      <h1 class="text-3xl text-center mb-4">Todo List</h1>
      <TodoList></TodoList>
    </div>
  </div>
</template>

<script setup lang="ts">
import TodoList from "./components/TodoList.vue";
</script>
