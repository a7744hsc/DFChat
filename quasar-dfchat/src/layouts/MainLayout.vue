<template>
  <q-layout view="hHh lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title> DF Chat 0.2</q-toolbar-title>
        <q-btn flat dense round icon="add" aria-label="New dialog" />
        <q-btn flat dense round icon="settings" aria-label="Settings" />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <ChatHistoryList />
    </q-drawer>

    <q-page-container class="absolute-full">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import ChatHistoryList from 'src/components/ChatHistoryList.vue';
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'MainLayout',
  setup() {
    const leftDrawerOpen = ref(false);
    return {
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value;
      },
    };
  },
  components: { ChatHistoryList },
});
</script>
