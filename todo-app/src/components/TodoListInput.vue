<template>
  <input
    type="text"
    class="border rounded px-2 py-1"
    v-model="content"
    @keydown.enter="addTodo"
    autofocus
  />
</template>

<script lang="ts" setup>
import { ref } from "vue";

const content = ref("");
const emit = defineEmits(["add-todo"]);

function addTodo() {
  if (content.value !== "") {
    emit("add-todo", content.value);
    content.value = "";
  }
}
</script>
