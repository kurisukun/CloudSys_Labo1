<template>
  <div>
    <ul>
      <li
          v-for="(todo, index) in todos"
          :key="index"
          class="
          border
          rounded
          px-2
          py-1
          mb-2
          flex
          items-center
          justify-between
          cursor-pointer
          hover:bg-gray-300
        "
          :class="{ 'line-through bg-red-200': todo.is_done }"
          @click.prevent="toggleTodo(todo)"
      >
        {{ todo.title }}
        <button
            class="ml-2 hover:text-red-600"
            @click.prevent.stop="deleteTodo(todo)"
        >
          <svg
              width="22"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
          >
            <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </li>
    </ul>
    <TodoListInput @add-todo="addTodo"></TodoListInput>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "@vue/reactivity";
import TodoListInput from "./TodoListInput.vue";
import axios from "axios";
import { Notyf } from "notyf";

interface TodoItem {
  id: number,
  title: string,
  is_done: boolean,
}

const notyf = new Notyf();

const todos = ref<TodoItem[]>([]);
fetchTodos();

function fetchTodos() {
  axios.get('http://localhost:8000/api/v1').then(res => {
    todos.value = res.data.map((item: any) => ({
      id: item.id,
      title: item.title,
      is_done: item.is_done,
    }));
  }).catch(err => {
    console.log(err);
    notyf.error(err.toString());
  })
}

function addTodo(content: string) {
  axios.post('http://localhost:8000/api/v1', {
    title: content,
    is_done: false,
  }).then(() => {
    fetchTodos();
  }).catch(err => {
    console.log(err);
    notyf.error(err.toString());
  });
}

function deleteTodo(item: TodoItem) {
  axios.delete(`http://localhost:8000/api/v1/${item.id}`).then(() => {
    fetchTodos();
  }).catch(err => {
    console.log(err);
    notyf.error(err.toString());
  })
}

function toggleTodo(item: TodoItem) {
  axios.put(`http://localhost:8000/api/v1/toggle/${item.id}`).then(() => {
    fetchTodos();
  }).catch(err => {
    console.log(err);
    notyf.error(err.toString());
  })
}
</script>
