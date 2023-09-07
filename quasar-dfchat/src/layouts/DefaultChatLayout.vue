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
        <q-btn
          flat
          dense
          label="New Chat"
          aria-label="New dialog"
          class="q-mr-sm"
          icon="add"
          @click="newChat"
        />
        <q-btn
          flat
          dense
          icon="delete"
          aria-label="delete"
          label="Delete Chat"
          @click="deleteCurrentChat"
        />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <ChatHistoryList
        @sendChat="changeChatContent"
        @chatHistoryChanged="updateHistoryList"
        :chats="chatHistoryList"
      />
    </q-drawer>

    <q-page-container class="absolute-full">
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
                    <q-tooltip>
                      Delete this message and all others below</q-tooltip
                    >
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
                  <div>
                    <q-markdown
                      v-if="message.content !== ''"
                      :src="message.content"
                    />
                    <q-spinner-dots
                      v-if="message.status === MessageStatus.Pending"
                      size="2rem"
                    />
                  </div>
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
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import ChatHistoryList from 'src/components/ChatHistoryList.vue';
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
  name: 'DefaultChatLayout',
  setup() {
    const leftDrawerOpen = ref(false);
    const $router = useRouter();
    const $q = useQuasar();
    const messages: Ref<Message[]> = ref([]);
    const userInput = ref('');
    const dialogId = ref<number | null>(null);
    const chatWindow = ref<HTMLDivElement | null>(null);
    const chatHistoryList = ref<
      { dialog_id: number; chat_history: Message[] }[]
    >([]);
    onMounted(async () => {
      if (localStorage.getItem('token') === null) {
        $router.push('/login');
      }
      chatHistoryList.value = (await api.get('/api/dialog')).data;
    });
    function updateHistoryList() {
      api.get('/api/dialog').then((response) => {
        chatHistoryList.value = response.data;
      });
    }
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
    function sendMessage(
      messagesList: Ref<Message[]>,
      inputValue: string,
      sse = true
    ) {
      if (inputValue.trim() === '') {
        console.log('empty message,ignore');
        return;
      }
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
      if (sse) {
        api
          .post(
            'api/gpt/sse',
            {
              dialog_id: dialogId.value,
              chat_history: messagesList.value,
            },
            {
              headers: {
                // 'Content-Type': 'text/event-stream',
              },
              async onDownloadProgress(progressEvent) {
                let resText = progressEvent.event.target.responseText;
                console.log('==========');
                console.log(resText);

                let lines = resText.substr(6).split('\r\ndata: '); // 去掉前面的"data: "，然后按照"\r\ndata: "分割
                let m = '';
                let ignoreNextLine = false;
                for (let i = 0; i < lines.length; i++) {
                  let line_str = lines[i];

                  if (ignoreNextLine) {
                    if (!line_str.endsWith('\r\nevent: ping')) {
                      ignoreNextLine = false;
                    }
                    continue;
                  }

                  if (line_str.startsWith(' ping')) {
                    // 处理起始行的"event: ping",但是前面有一个substr(6),所以
                    ignoreNextLine = true;
                    continue;
                  }

                  if (line_str.endsWith('\r\nevent: ping')) {
                    //这是为了解决返回中包含ping的event
                    line_str = line_str.substr(0, line_str.length - 13);
                    ignoreNextLine = true;
                  }

                  if (line_str.length >= 2 && line_str.substr(-2) == '\r\n') {
                    // openai的返回有时会包含一组\r\n，有时会包含两组\r\n，这里会去除掉第二组\r\n
                    line_str = line_str.substr(0, line_str.length - 2);
                  }
                  if (line_str != '') {
                    m += line_str;
                  } else {
                    m += '\n'; // 对于内容为空的行，应该为原文加一个回车符号
                  }
                }
                let lastMessage = messagesList.value.at(-1);
                if (lastMessage) {
                  lastMessage.content = m;
                }

                if (chatWindow.value !== null) {
                  await nextTick();
                  chatWindow.value.scrollTop = chatWindow.value.scrollHeight;
                }
              },
            }
          )
          .then(() => {
            let lastMessage = messagesList.value.at(-1);
            if (lastMessage) {
              lastMessage.status = MessageStatus.Ok;
            }
            //save dialog for new chat
            if (dialogId.value === null) {
              api
                .post('/api/dialog', {
                  dialog_id: dialogId.value,
                  chat_history: messagesList.value,
                })
                .then((response) => {
                  console.log('save dialog response:', response);
                  dialogId.value = response.data.dialog_id;
                })
                .catch((error) => {
                  console.log(error);
                  $q.notify({
                    color: 'negative',
                    message: '保存对话失败',
                  });
                });
            }
            updateHistoryList();
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
      } else {
        api
          .post('/api/gpt/standard', {
            dialog_id: dialogId.value,
            chat_history: messagesList.value,
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
      MessageStatus,
      chatWindow,
      userInput: userInput,
      chatHistoryList,
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
      changeChatContent(chat: { dialog_id: number; chat_history: Message[] }) {
        messages.value = chat.chat_history;
        dialogId.value = chat.dialog_id;
      },
      updateHistoryList,
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value;
      },
      deleteCurrentChat() {
        if (dialogId.value === null) {
          messages.value = [];
        }
        api
          .delete('/api/dialog/id/' + dialogId.value?.toString())
          .then(() => {
            $q.notify({
              color: 'positive',
              message: '删除对话成功',
            });
            dialogId.value = null;
            messages.value = [];
            updateHistoryList();
          })
          .catch((error) => {
            console.log(error);
            $q.notify({
              color: 'negative',
              message: '删除对话失败',
            });
          });
      },
    };
  },
  components: { ChatHistoryList },
});
export { MessageStatus };
export type { Message };
</script>
