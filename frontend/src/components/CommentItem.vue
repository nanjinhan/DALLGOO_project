<script setup>
import { ref } from 'vue'

import { adminApi } from '@/api/admin'
import { commentApi } from '@/api/comment'
import { useAuthStore } from '@/stores/auth'
import { errorMessage, formatDate } from '@/utils/format'

const props = defineProps({
  comment: { type: Object, required: true },
  postId: { type: [Number, String], required: true },
  depth: { type: Number, default: 0 },
})
const emit = defineEmits(['changed'])

const auth = useAuthStore()
const isOwner = () =>
  auth.isLoggedIn && props.comment.author?.id === auth.user?.id

const editing = ref(false)
const editText = ref('')
const replying = ref(false)
const replyText = ref('')
const busy = ref(false)
const error = ref('')

function startEdit() {
  editText.value = props.comment.content
  editing.value = true
}

async function saveEdit() {
  if (!editText.value.trim()) return
  busy.value = true
  error.value = ''
  try {
    await commentApi.update(props.comment.id, editText.value.trim())
    editing.value = false
    emit('changed')
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

async function remove() {
  if (!confirm('댓글을 삭제할까요?')) return
  busy.value = true
  try {
    await commentApi.remove(props.comment.id)
    emit('changed')
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

async function adminRemove() {
  if (!confirm('[관리자] 이 댓글을 강제 삭제할까요?')) return
  busy.value = true
  try {
    await adminApi.deleteComment(props.comment.id)
    emit('changed')
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

async function toggleLike() {
  if (!auth.isLoggedIn) {
    error.value = '로그인이 필요합니다.'
    return
  }
  try {
    if (props.comment.liked_by_me) await commentApi.unlike(props.comment.id)
    else await commentApi.like(props.comment.id)
    emit('changed')
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function submitReply() {
  if (!replyText.value.trim()) return
  busy.value = true
  error.value = ''
  try {
    await commentApi.create(props.postId, {
      content: replyText.value.trim(),
      parent_id: props.comment.id,
    })
    replyText.value = ''
    replying.value = false
    emit('changed')
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="comment" :class="{ reply: depth > 0 }">
    <div class="head">
      <span class="nick">{{ comment.author?.nickname || '(알수없음)' }}</span>
      <span class="muted">{{ formatDate(comment.created_at) }}</span>
    </div>

    <div v-if="editing" class="edit-box">
      <textarea v-model="editText" class="textarea short" />
      <div class="row">
        <button class="btn btn-primary" :disabled="busy" @click="saveEdit">저장</button>
        <button class="btn" @click="editing = false">취소</button>
      </div>
    </div>
    <p v-else class="body" :class="{ deleted: comment.is_deleted }">
      {{ comment.content }}
    </p>

    <div v-if="!comment.is_deleted" class="actions">
      <button class="link" :class="{ liked: comment.liked_by_me }" @click="toggleLike">
        ❤ {{ comment.like_count }}
      </button>
      <button v-if="depth === 0 && auth.isLoggedIn" class="link" @click="replying = !replying">
        답글
      </button>
      <template v-if="isOwner()">
        <button class="link" @click="startEdit">수정</button>
        <button class="link danger" @click="remove">삭제</button>
      </template>
      <button
        v-else-if="auth.isAdmin"
        class="link danger"
        @click="adminRemove"
      >
        관리자 삭제
      </button>
    </div>
    <p v-if="error" class="error-text">{{ error }}</p>

    <div v-if="replying" class="reply-box">
      <textarea
        v-model="replyText"
        class="textarea short"
        placeholder="답글을 입력하세요"
      />
      <div class="row">
        <button class="btn btn-primary" :disabled="busy" @click="submitReply">
          답글 등록
        </button>
        <button class="btn" @click="replying = false">취소</button>
      </div>
    </div>

    <!-- 대댓글 (1단계) -->
    <div v-if="comment.replies?.length" class="replies">
      <CommentItem
        v-for="child in comment.replies"
        :key="child.id"
        :comment="child"
        :post-id="postId"
        :depth="depth + 1"
        @changed="emit('changed')"
      />
    </div>
  </div>
</template>

<style scoped>
.comment {
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}
.comment.reply {
  border-bottom: none;
  border-left: 2px solid var(--border);
  margin-left: 8px;
  padding: 12px 0 4px 14px;
}
.head {
  display: flex;
  gap: 8px;
  align-items: baseline;
  margin-bottom: 6px;
}
.nick {
  font-weight: 700;
  font-size: 14px;
}
.body {
  margin: 0 0 8px;
  font-size: 14px;
  line-height: 1.55;
  white-space: pre-wrap;
}
.body.deleted {
  color: var(--muted);
  font-style: italic;
}
.actions {
  display: flex;
  gap: 12px;
}
.link {
  border: none;
  background: none;
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
  padding: 0;
}
.link:hover {
  color: var(--text);
}
.link.liked {
  color: var(--danger);
}
.link.danger:hover {
  color: var(--danger);
}
.edit-box,
.reply-box {
  margin: 8px 0;
}
.textarea.short {
  min-height: 70px;
  margin-bottom: 8px;
}
.replies {
  margin-top: 8px;
}
</style>
