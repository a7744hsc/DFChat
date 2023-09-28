<template>
  <q-page padding class="">
    <!-- content -->
    <div class="q-gutter-md q-layout-column">
      <h2 class="text-center text-primary">用户登录</h2>
    </div>

    <q-card
      style="
        /* max-width: 800px; */
        /* display: flex; */
        /* justify-content: center; */
        /* align-items: center; */
      "
    >
      <q-card-section>
        <q-input v-model="userName" label="User Name"></q-input>
      </q-card-section>
      <q-card-section>
        <q-input v-model="password" type="password" label="Password"></q-input>
      </q-card-section>

      <q-card-actions align="evenly">
        <q-btn label="Register" color="primary" @click="register" />
        <q-btn label="Login" color="primary" @click="login" />
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
  name: 'LoginPage',

  setup() {
    const $q = useQuasar();
    const $router = useRouter();
    const userName = ref('');
    const password = ref('');
    const email = ref('');
    const invitationCode = ref('');
    function login() {
      api
        .post('/api/user/login', {
          username: userName.value,
          password: password.value,
        })
        .then((response) => {
          console.log(response);
          api.defaults.headers.common.Authorization = `Bearer ${response.data.token}`;
          localStorage.setItem('token', response.data.access_token);
          $q.notify({
            color: 'positive',
            message: 'Login success',
          });
          $router.push('/');
        })
        .catch((error) => {
          //check if error is an axios reject error
          if (error.response === undefined) {
            $q.notify({
              color: 'negative',
              message: error,
            });
            return;
          }

          $q.notify({
            color: 'negative',
            message: error.response.data.detail,
          });
        });
    }
    function register() {
      $router.push('/login/register');
    }

    return {
      userName,
      password,
      email,
      invitationCode,
      login,
      register,
    };
  },
});
</script>
