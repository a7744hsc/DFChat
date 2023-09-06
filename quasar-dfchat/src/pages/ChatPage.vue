<template>
  <q-page flex style="" class="q-pa-sm fit flex">
    <div
      id="chat-window"
      flex
      class="scroll justify-center flex"
      style="position: relative; height: 100%; width: 100%"
      ref="chatWindow"
    >
      <div id="chat-items" style="max-width: 800px" class="fit">
        <div
          class="chat-item"
          v-for="message in messages"
          :key="message.sequence"
        >
          <div
            v-if="message.sent_by_user"
            style="max-width: 95%"
            class="user-content float-right"
          >
            <div class="col-auto float-left q-mr-xs">
              <q-btn
                round
                dense
                color="primary"
                size="xs"
                icon="delete"
                class="block"
                @click="deleteMessage(message.sequence)"
              >
                <q-tooltip> Delete this message and all others below</q-tooltip>
              </q-btn>
              <q-btn
                round
                dense
                color="primary"
                size="xs"
                icon="replay"
                class="block"
                @click="resendMessage(message.sequence)"
              >
                <q-tooltip>
                  Resend this message, all message below will be lost
                </q-tooltip>
              </q-btn>
            </div>
            <q-chat-message
              :sent="message.sent_by_user"
              class="col-auto float-right text-xl"
            >
              <div style="white-space: pre-wrap">
                {{ message.content }}
              </div>
            </q-chat-message>
          </div>
          <div v-else class="bot-content">
            <q-chat-message
              :sent="message.sent_by_user"
              style="max-width: 90%"
              class="float-left"
            >
              <!-- show markdown if content not empty,else show spinner -->
              <q-spinner-dots v-if="message.content === ''" size="2rem" />
              <q-markdown v-else :src="message.content" />
            </q-chat-message>
          </div>
          <!-- This is used to avoid outter div collapse -->
          <div style="clear: both"></div>
        </div>
      </div>
    </div>

    <q-footer>
      <q-input
        outlined
        bottom-slots
        v-model="userInput"
        counter
        maxlength="2048"
        :dense="true"
        type="textarea"
        :input-style="{ height: '100px' }"
        @keypress="keypressHandler"
        bg-color="white"
      >
        <template v-slot:append>
          <q-icon
            v-if="userInput !== ''"
            name="close"
            @click="userInput = ''"
            class="cursor-pointer"
          />
        </template>
        <template v-slot:after>
          <q-btn round dense flat icon="send" @click="sendMessage" />
        </template>
      </q-input>
    </q-footer>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, nextTick, Ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { api } from 'src/boot/axios';
import { useQuasar } from 'quasar';

enum MessageStatus {
  Ok,
  Pending,
  Error,
}
type Message = {
  sequence: number;
  sent_by_user: boolean;
  content: string;
  status: MessageStatus;
};

export default defineComponent({
  name: 'ChatPage',
  setup() {
    const $router = useRouter();
    const $q = useQuasar();
    const messages: Ref<Message[]> = ref([]);
    const userInput = ref('');
    const dialogId = ref<number | null>(null);
    const chatWindow = ref<HTMLDivElement | null>(null);
    onMounted(() => {
      if (localStorage.getItem('token') === null) {
        $router.push('/login');
      }
    });
    api.defaults.headers.common.Authorization = `Bearer ${localStorage.getItem(
      'token'
    )}`;
    watch(
      messages,
      async () => {
        if (chatWindow.value !== null) {
          await nextTick();
          chatWindow.value.scrollTop = chatWindow.value.scrollHeight;
        }
      },
      { deep: true }
    );
    function sendMessage(messagesList: Ref<Message[]>, inputValue: string) {
      let message_seq = messagesList.value.length + 1;
      messagesList.value.push({
        sequence: message_seq,
        sent_by_user: true,
        content: inputValue,
        status: MessageStatus.Ok,
      });
      message_seq += 1;
      const botMessage = {
        sequence: message_seq,
        sent_by_user: false,
        content: '',
        status: MessageStatus.Pending,
      };
      messagesList.value.push(botMessage);
      console.log('Sending llm request:', {
        dialog_id: dialogId.value,
        prompt: inputValue,
      });
      api
        .post('/api/gpt/standard', {
          dialog_id: dialogId.value,
          chat_history: messagesList.value,
          prompt: inputValue,
        })
        .then((response) => {
          console.log('Receiving llm response:', response);
          dialogId.value = response.data.dialog_id;
          let chatHistory = response.data.chat_history as Message[];
          messagesList.value.pop();
          let lastMessage = chatHistory.at(-1);
          if (lastMessage !== undefined) {
            messagesList.value.push(lastMessage);
          } else {
            console.error('Empty chat history received');
          }
        })
        .catch((error) => {
          botMessage.status = MessageStatus.Error;
          botMessage.content = error.response.data.tostring();
          console.log(error);
          $q.notify({
            color: 'negative',
            message: error.response.data.tostring(),
          });
        });
    }
    async function keypressHandler(e: KeyboardEvent) {
      if (e.key === 'Enter' && e.shiftKey) {
        e.preventDefault();
        console.log('shift enter');
        const input = e.target as HTMLTextAreaElement;
        const start = input.selectionStart;
        const end = input.selectionEnd;
        const oldValue = userInput.value;

        userInput.value = oldValue.slice(0, start) + '\n' + oldValue.slice(end);
        await nextTick();
        input.selectionStart = input.selectionEnd = start + 1;
      } else if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage(messages, userInput.value);
        userInput.value = '';
      }
    }
    return {
      messages,
      chatWindow,
      userInput: userInput,
      keypressHandler,
      sendMessage() {
        sendMessage(messages, userInput.value);
        userInput.value = '';
      },
      deleteMessage(sequence: number) {
        messages.value = messages.value.filter((message) => {
          return message.sequence < sequence;
        });
        let requestUrl =
          '/api/dialog/id/' +
          dialogId.value?.toString() +
          '/sequence/' +
          sequence.toString();
        api.delete(requestUrl).catch((error) => {
          console.log(error);
          $q.notify({
            color: 'negative',
            message: '删除失败，前后端数据可能不一致，请刷新页面',
          });
        });
      },
      resendMessage(sequence: number) {
        let messageToSent = messages.value.at(sequence - 1) as Message;
        messages.value = messages.value.filter((message) => {
          return message.sequence < sequence;
        });
        sendMessage(messages, messageToSent.content);
      },
      newChat() {
        messages.value = [];
        dialogId.value = null;
      },
    };
  },
});
</script>
<style lang="scss" scoped></style>
