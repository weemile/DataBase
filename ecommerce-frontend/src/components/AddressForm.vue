<template>
  <el-form 
    ref="formRef" 
    :model="form" 
    :rules="rules" 
    label-width="100px"
  >
    <el-form-item label="收货人" prop="receiver_name">
      <el-input 
        v-model="form.receiver_name" 
        placeholder="请输入收货人姓名"
        maxlength="20"
        show-word-limit
      />
    </el-form-item>
    
    <el-form-item label="手机号" prop="receiver_phone">
      <el-input 
        v-model="form.receiver_phone" 
        placeholder="请输入11位手机号"
        maxlength="11"
      />
    </el-form-item>
    
    <el-form-item label="所在省份" prop="province">
      <el-input 
        v-model="form.province" 
        placeholder="请输入省份，如：北京市、广东省"
        maxlength="20"
      />
    </el-form-item>

    <el-form-item label="所在城市" prop="city">
      <el-input 
        v-model="form.city" 
        placeholder="请输入城市，如：北京市、广州市"
        maxlength="20"
      />
    </el-form-item>

    <el-form-item label="所在区县" prop="district">
      <el-input 
        v-model="form.district" 
        placeholder="请输入区县，如：朝阳区、天河区"
        maxlength="20"
      />
    </el-form-item>
    
    <el-form-item label="详细地址" prop="detail_address">
      <el-input
        v-model="form.detail_address"
        type="textarea"
        :rows="3"
        placeholder="请输入详细地址，如街道、小区、楼栋号、单元室等"
        maxlength="200"
        show-word-limit
      />
    </el-form-item>
    
    <el-form-item label="邮政编码" prop="postal_code">
      <el-input 
        v-model="form.postal_code" 
        placeholder="请输入6位邮政编码"
        maxlength="6"
      />
    </el-form-item>
    
    <el-form-item label="设为默认" prop="is_default">
      <el-switch v-model="form.is_default" />
      <span class="switch-label">设置为默认收货地址</span>
    </el-form-item>
  </el-form>
  
  <div class="form-actions">
    <el-button @click="cancel">取消</el-button>
    <el-button type="primary" @click="save">保存</el-button>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  address: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'cancel'])

const formRef = ref(null)

// 表单数据
const form = reactive({
  receiver_name: '',
  receiver_phone: '',
  province: '',
  city: '',
  district: '',
  detail_address: '',
  postal_code: '',
  is_default: false
})

// 表单验证规则
const rules = {
  receiver_name: [
    { required: true, message: '请输入收货人姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在2-20个字符之间', trigger: 'blur' }
  ],
  receiver_phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  province: [
    { required: true, message: '请输入省份', trigger: 'blur' },
    { min: 2, max: 20, message: '省份长度在2-20个字符之间', trigger: 'blur' }
  ],
  city: [
    { required: true, message: '请输入城市', trigger: 'blur' },
    { min: 2, max: 20, message: '城市长度在2-20个字符之间', trigger: 'blur' }
  ],
  district: [
    { required: true, message: '请输入区县', trigger: 'blur' },
    { min: 2, max: 20, message: '区县长度在2-20个字符之间', trigger: 'blur' }
  ],
  detail_address: [
    { required: true, message: '请输入详细地址', trigger: 'blur' },
    { min: 5, max: 200, message: '地址长度在5-200个字符之间', trigger: 'blur' }
  ],
  postal_code: [
    { pattern: /^\d{6}$/, message: '请输入6位邮政编码', trigger: 'blur' }
  ]
}

// 保存表单
const save = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 构建地址数据
    const addressData = {
      receiver_name: form.receiver_name,
      receiver_phone: form.receiver_phone,
      province: form.province,
      city: form.city,
      district: form.district,
      detail_address: form.detail_address,
      postal_code: form.postal_code,
      is_default: form.is_default
    }
    
    // 转换 is_default: Boolean → 0/1
    const sendData = {
      ...addressData,
      is_default: form.is_default ? 1 : 0
    }
    
    // 如果是编辑模式，保留原始ID
    if (props.address && props.address.address_id) {
      sendData.address_id = props.address.address_id
    }
    
    console.log('📝 提交地址数据:', sendData)
    emit('save', sendData)
    
  } catch (error) {
    console.error('表单验证失败', error)
    if (error && error.fields) {
      // 如果有具体的字段错误
      const firstError = Object.values(error.fields)[0][0].message
      ElMessage.error(firstError)
    } else {
      ElMessage.error('请检查表单填写是否正确')
    }
  }
}

const cancel = () => {
  emit('cancel')
}

// 如果传入地址，填充表单
onMounted(() => {
  if (props.address) {
    // 复制地址数据
    Object.assign(form, props.address)
    form.is_default = props.address.is_default === 1
    
    console.log('📋 编辑地址数据:', props.address)
  }
})
</script>

<style scoped>
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.switch-label {
  margin-left: 10px;
  color: #606266;
  font-size: 14px;
}

:deep(.el-textarea__inner) {
  resize: vertical;
}
</style>