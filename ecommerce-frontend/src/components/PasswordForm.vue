<template>
  <el-form :model="form" label-width="100px" ref="formRef" :rules="rules">
    <el-form-item label="当前密码" prop="currentPassword">
      <el-input v-model="form.currentPassword" type="password" show-password />
    </el-form-item>
    <el-form-item label="新密码" prop="newPassword">
      <el-input v-model="form.newPassword" type="password" show-password />
    </el-form-item>
    <el-form-item label="确认密码" prop="confirmPassword">
      <el-input v-model="form.confirmPassword" type="password" show-password />
    </el-form-item>
  </el-form>
  <div class="form-actions">
    <el-button @click="cancel">取消</el-button>
    <el-button type="primary" @click="save">保存</el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['save', 'cancel'])

const form = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const formRef = ref(null)

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.value.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const save = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    emit('save', form.value)
    ElMessage.success('密码修改成功')
  } catch (error) {
    console.error('表单验证失败', error)
  }
}

const cancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>