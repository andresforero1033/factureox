from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from db import collection, ObjectId
from datetime import datetime

news_bp = Blueprint('news', __name__, url_prefix='/noticias')


def _is_admin():
    role = getattr(current_user, 'role', 'user') if getattr(current_user, 'is_authenticated', False) else 'user'
    return str(role).lower() in ('admin', 'owner')


@news_bp.route('/')
def list_news():
    page = max(int(request.args.get('page', 1) or 1), 1)
    per_page = min(max(int(request.args.get('per_page', 9) or 9), 3), 24)
    skip = (page - 1) * per_page
    q = {}
    items = list(collection('news').find(q).sort('created_at', -1).skip(skip).limit(per_page))
    total = collection('news').count_documents(q)
    for it in items:
        it['id'] = str(it['_id'])
    return render_template('noticias_list.html', items=items, page=page, per_page=per_page, total=total)


@news_bp.route('/<id>')
def detail_news(id):
    try:
        doc = collection('news').find_one({'_id': ObjectId(id)})
    except Exception:
        doc = None
    if not doc:
        flash('La noticia no existe o fue eliminada.', 'warning')
        return redirect(url_for('news.list_news'))
    doc['id'] = str(doc.get('_id'))
    return render_template('noticias_detail.html', item=doc)


@news_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def create_news():
    if not _is_admin():
        flash('No tienes permisos para crear noticias.', 'danger')
        return redirect(url_for('news.list_news'))
    if request.method == 'POST':
        title = (request.form.get('title') or '').strip()
        content = (request.form.get('content') or '').strip()
        summary = (request.form.get('summary') or '').strip()
        image_url = (request.form.get('image_url') or '').strip()
        published = bool(request.form.get('published'))
        if not title or not content:
            flash('Título y contenido son obligatorios.', 'warning')
            return render_template('noticias_form.html', mode='create', data=request.form)
        if not summary:
            summary = (content[:220] + '…') if len(content) > 220 else content
        author = getattr(current_user, 'name', None) or getattr(current_user, 'username', None) or 'Admin'
        now = datetime.utcnow()
        res = collection('news').insert_one({
            'title': title,
            'summary': summary,
            'content': content,
            'author': author,
            'image_url': image_url or None,
            'published': published,
            'created_at': now,
            'updated_at': now,
        })
        flash('Noticia creada.', 'success')
        return redirect(url_for('news.detail_news', id=str(res.inserted_id)))
    return render_template('noticias_form.html', mode='create', data={})


@news_bp.route('/<id>/editar', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    if not _is_admin():
        flash('No tienes permisos para editar noticias.', 'danger')
        return redirect(url_for('news.list_news'))
    try:
        doc = collection('news').find_one({'_id': ObjectId(id)})
    except Exception:
        doc = None
    if not doc:
        flash('La noticia no existe.', 'warning')
        return redirect(url_for('news.list_news'))
    if request.method == 'POST':
        title = (request.form.get('title') or '').strip()
        content = (request.form.get('content') or '').strip()
        summary = (request.form.get('summary') or '').strip()
        image_url = (request.form.get('image_url') or '').strip()
        published = bool(request.form.get('published'))
        if not title or not content:
            flash('Título y contenido son obligatorios.', 'warning')
            return render_template('noticias_form.html', mode='edit', data=request.form, item=doc)
        if not summary:
            summary = (content[:220] + '…') if len(content) > 220 else content
        collection('news').update_one({'_id': doc['_id']}, {'$set': {
            'title': title,
            'summary': summary,
            'content': content,
            'image_url': image_url or None,
            'published': published,
            'updated_at': datetime.utcnow()
        }})
        flash('Noticia actualizada.', 'success')
        return redirect(url_for('news.detail_news', id=id))
    doc['id'] = str(doc['_id'])
    return render_template('noticias_form.html', mode='edit', item=doc, data=doc)


@news_bp.route('/<id>/eliminar', methods=['POST'])
@login_required
def delete_news(id):
    if not _is_admin():
        flash('No tienes permisos para eliminar noticias.', 'danger')
        return redirect(url_for('news.list_news'))
    try:
        collection('news').delete_one({'_id': ObjectId(id)})
        flash('Noticia eliminada.', 'info')
    except Exception:
        flash('No se pudo eliminar la noticia.', 'danger')
    return redirect(url_for('news.list_news'))
