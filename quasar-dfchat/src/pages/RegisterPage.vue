<template>
  <q-page padding class="">
    <!-- content -->
    <div class="q-gutter-md q-layout-column">
      <h1 class="text-h2 text-center">用户注册</h1>
    </div>
    <q-card>
      <q-card-section>
        <q-input v-model="userName" label="User Name"></q-input>
      </q-card-section>
      <q-card-section>
        <q-input v-model="email" label="Email" type="email"></q-input>
      </q-card-section>
      <q-card-section>
        <q-input v-model="invitationCode" label="Invitation Code"></q-input>
      </q-card-section>
      <q-card-section>
        <q-input v-model="password" type="password" label="Password"></q-input>
      </q-card-section>

      <q-card-actions align="evenly">
        <q-btn label="Register" color="primary" @click="register" />
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script lang="ts">
import { api } from 'src/boot/axios';
import { defineComponent, resolveDirective } from 'vue';
import { ref } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
export default defineComponent({
  name: 'RegisterPage',

  setup() {
    const $q = useQuasar();
    const $router = useRouter();
    const userName = ref('');
    const password = ref('');
    const email = ref('');
    const invitationCode = ref('');
    function register() {
      api
        .post('/api/user/register', {
          username: userName.value,
          password: password.value,
          email: email.value,
          invitation_code: invitationCode.value,
        })
        .then(() => {
          $q.notify({
            color: 'positive',
            message: 'Register success, please login',
          });
          $router.push('/login');
        })
        .catch((error) => {
          $q.notify({
            color: 'negative',
            message: error.response.data.detail,
          });
        });
    }

    return {
      userName,
      password,
      email,
      invitationCode,
      register,
    };
  },
});
</script>
