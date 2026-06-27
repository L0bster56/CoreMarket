'use client'

import Link from 'next/link'
import { useState, useCallback, memo } from 'react'
import { useAuth } from '@/lib/auth-context'
import { listComments, createComment, updateComment, deleteComment } from '@/services/comments'
import type { ApiComment } from '@/types'

interface CommentItemProps {
  comment: ApiComment
  depth: number
  userId: string | undefined
  userRole: string | undefined
  itemId: string
  onMutate: () => Promise<void>
}

const CommentItem = memo(function CommentItem({
  comment,
  depth,
  userId,
  userRole,
  itemId,
  onMutate,
}: CommentItemProps) {
  const [replyOpen, setReplyOpen] = useState(false)
  const [replyBody, setReplyBody] = useState('')
  const [editOpen, setEditOpen] = useState(false)
  const [editBody, setEditBody] = useState(comment.body)
  const [submitting, setSubmitting] = useState(false)

  const isOwner = userId === comment.user_id
  const isAdmin = userRole === 'admin'
  const canEdit = isOwner && !comment.is_deleted
  const canDelete = (isOwner || isAdmin) && !comment.is_deleted
  const loggedIn = !!userId

  const handleReply = async () => {
    if (!replyBody.trim()) return
    setSubmitting(true)
    try {
      await createComment(itemId, replyBody.trim(), comment.id)
      setReplyOpen(false)
      setReplyBody('')
      await onMutate()
    } catch {
      // silent
    } finally {
      setSubmitting(false)
    }
  }

  const handleSaveEdit = async () => {
    if (!editBody.trim()) return
    setSubmitting(true)
    try {
      await updateComment(itemId, comment.id, editBody.trim())
      setEditOpen(false)
      await onMutate()
    } catch {
      // silent
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Удалить комментарий?')) return
    setSubmitting(true)
    try {
      await deleteComment(itemId, comment.id)
      await onMutate()
    } catch {
      // silent
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className={depth > 0 ? 'mt-3 ml-6 pl-4 border-l-2 border-gray-100' : ''}>
      <div className="bg-white rounded-2xl border border-gray-200 p-5">
        <div className="flex items-start gap-2 mb-3">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
              depth === 0 ? 'bg-indigo-100' : 'bg-gray-100'
            }`}
          >
            <span
              className={`text-xs font-bold ${depth === 0 ? 'text-indigo-600' : 'text-gray-500'}`}
            >
              U
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center flex-wrap gap-2">
              <span className="text-xs text-gray-400 font-mono">{comment.user_id.slice(0, 8)}…</span>
              <span className="text-xs text-gray-400">
                {new Date(comment.created_at).toLocaleDateString('ru-RU')}
              </span>
              {loggedIn && !comment.is_deleted && (
                <div className="ml-auto flex items-center gap-3 flex-shrink-0">
                  {canEdit && (
                    <button
                      onClick={() => { setEditOpen(true); setEditBody(comment.body) }}
                      className="text-xs text-indigo-600 hover:underline"
                    >
                      Изменить
                    </button>
                  )}
                  {canDelete && (
                    <button
                      onClick={handleDelete}
                      disabled={submitting}
                      className="text-xs text-red-500 hover:underline disabled:opacity-50"
                    >
                      Удалить
                    </button>
                  )}
                  <button
                    onClick={() => setReplyOpen((o) => !o)}
                    className="text-xs text-gray-500 hover:text-indigo-600 hover:underline"
                  >
                    Ответить
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {editOpen ? (
          <div className="space-y-2">
            <textarea
              value={editBody}
              onChange={(e) => setEditBody(e.target.value)}
              className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-300"
              rows={3}
              autoFocus
            />
            <div className="flex gap-2">
              <button
                onClick={handleSaveEdit}
                disabled={submitting || !editBody.trim()}
                className="px-4 py-1.5 bg-indigo-600 text-white text-xs rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                Сохранить
              </button>
              <button
                onClick={() => setEditOpen(false)}
                className="px-4 py-1.5 border border-gray-200 text-xs rounded-lg hover:bg-gray-50"
              >
                Отмена
              </button>
            </div>
          </div>
        ) : (
          <p className="text-gray-700 text-sm leading-relaxed">
            {comment.is_deleted ? (
              <em className="text-gray-400">Комментарий удалён</em>
            ) : (
              comment.body
            )}
          </p>
        )}
      </div>

      {replyOpen && (
        <div className="ml-6 mt-2 pl-4 border-l-2 border-indigo-100">
          <div className="space-y-2">
            <textarea
              value={replyBody}
              onChange={(e) => setReplyBody(e.target.value)}
              placeholder="Ваш ответ..."
              className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-300"
              rows={3}
              autoFocus
            />
            <div className="flex gap-2">
              <button
                onClick={handleReply}
                disabled={submitting || !replyBody.trim()}
                className="px-4 py-1.5 bg-indigo-600 text-white text-xs rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                Ответить
              </button>
              <button
                onClick={() => setReplyOpen(false)}
                className="px-4 py-1.5 border border-gray-200 text-xs rounded-lg hover:bg-gray-50"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}

      {comment.children.length > 0 && (
        <div>
          {comment.children.map((child) => (
            <CommentItem
              key={child.id}
              comment={child}
              depth={depth + 1}
              userId={userId}
              userRole={userRole}
              itemId={itemId}
              onMutate={onMutate}
            />
          ))}
        </div>
      )}
    </div>
  )
})

interface Props {
  itemId: string
  initialComments: ApiComment[]
}

export default function CommentsSection({ itemId, initialComments }: Props) {
  const { user } = useAuth()
  const [comments, setComments] = useState<ApiComment[]>(initialComments)
  const [newBody, setNewBody] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    const fresh = await listComments(itemId)
    setComments(fresh)
  }, [itemId])

  const handleCreate = async () => {
    if (!newBody.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      await createComment(itemId, newBody.trim())
      setNewBody('')
      await refresh()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      {user ? (
        <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-6">
          <textarea
            value={newBody}
            onChange={(e) => setNewBody(e.target.value)}
            placeholder="Напишите комментарий..."
            className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-300"
            rows={3}
          />
          {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
          <div className="mt-2 flex justify-end">
            <button
              onClick={handleCreate}
              disabled={submitting || !newBody.trim()}
              className="px-5 py-2 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {submitting ? 'Отправка…' : 'Отправить'}
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-6">
          <p className="text-sm text-gray-500">
            <Link href="/login" className="text-indigo-600 hover:underline">
              Войдите
            </Link>{' '}
            чтобы оставить комментарий
          </p>
        </div>
      )}

      {comments.length === 0 ? (
        <p className="text-gray-500 text-center py-8">Пока нет комментариев. Будьте первым!</p>
      ) : (
        <div className="space-y-4">
          {comments.map((c) => (
            <CommentItem
              key={c.id}
              comment={c}
              depth={0}
              userId={user?.id}
              userRole={user?.role}
              itemId={itemId}
              onMutate={refresh}
            />
          ))}
        </div>
      )}
    </div>
  )
}
