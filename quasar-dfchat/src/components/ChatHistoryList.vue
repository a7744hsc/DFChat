<template>
  <q-list>
    <q-item-label header>
      Chat History
      <q-btn
        icon="delete"
        class="float-right"
        aria-label="clear history"
        color="red"
        @click="confirm = true"
      >
        <q-tooltip> Clear all chat history </q-tooltip>
      </q-btn>
    </q-item-label>
    <q-dialog v-model="confirm" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <span class="q-ml-sm"
            >You are clearing all chat histories， this is not undoable！</span
          >
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
          <q-btn
            flat
            label="Confirm"
            color="primary"
            @click="clearChatHistory"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <div v-for="chat in chats" :key="chat.dialog_id">
      <q-btn
        style="width: 100%; justify-content: left"
        @click="handleChatHistoryClick(chat)"
      >
        <q-item-label>{{
          chat.chat_history[0].content.length < 50
            ? chat.chat_history[0].content
            : chat.chat_history[0].content.substring(0, 50) + '...'
        }}</q-item-label>
      </q-btn>
    </div>
  </q-list>
</template>

<script lang="ts">
import { PropType, defineComponent, onMounted, ref } from 'vue';
import { Message } from 'layouts/DefaultChatLayout.vue';
import { api } from 'boot/axios';
import { useQuasar } from 'quasar';

const $q = useQuasar();
export default defineComponent({
  name: 'ChatHistoryList',
  props: {
    chats: Array as PropType<{ dialog_id: number; chat_history: Message[] }[]>,
  },
  setup(props, { emit }) {
    // const chatHistoryList = ref<
    // { dialog_id: number; chat_history: Message[] }[]
    // >([]);
    onMounted(async () => {
      // let res = await api.get('/api/dialog');
      // chatHistoryList.value = res.data;
    });
    const clearChatHistory = async () => {
      try {
        let res = await api.delete('/api/dialog');
        emit('chatHistoryChanged');
        console.log(res);
      } catch (e) {
        console.log(e);
        $q.notify({
          color: 'negative',
          message: 'Error clearing chat history',
        });
      }
    };
    return {
      clearChatHistory,
      confirm: ref(false),
    };
  },
  methods: {
    handleChatHistoryClick(chat: {
      dialog_id: number;
      chat_history: Message[];
    }) {
      this.$emit('sendChat', chat);
    },
  },
});
</script>
