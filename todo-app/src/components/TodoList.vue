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
        :class="{ 'line-through bg-red-200': todo.done }"
        @click="() => toggleTodo(index)"
      >
        {{ todo.name }}
        <button
          class="ml-2 hover:text-red-600"
          @click="(e) => deleteTodo(index, e)"
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

interface TodoItem {
  name: string;
  done: boolean;
}

const todos = ref<TodoItem[]>([
  {
    name: "Todo list item 1",
    done: false,
  },
  {
    name: "Todo list item 2",
    done: false,
  },
  {
    name: "Todo list item 3",
    done: false,
  },
  {
    name: "Todo list item 4",
    done: false,
  },
]);

function addTodo(content: string) {
  todos.value.push({
    name: content,
    done: false,
  });
}

function deleteTodo(index: number, e: MouseEvent) {
  e.preventDefault();
  e.stopPropagation();
  todos.value = todos.value.filter((todo, i) => {
    return i !== index;
  });
}

function toggleTodo(index: number) {
  todos.value = todos.value.map((todo, i) => {
    if (i === index) {
      todo.done = !todo.done;
    }
    return todo;
  });
}
</script>
