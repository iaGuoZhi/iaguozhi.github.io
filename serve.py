import livereload

import build_blogs
import build_photos


def rebuild_blogs():
    build_blogs.main()


def rebuild_photos():
    build_photos.main()


server = livereload.Server()
server.setHeader("Cache-Control", "no-store")
server.watch("blogs/*.md", rebuild_blogs)
server.watch("photos/*.md", rebuild_photos)
server.watch("docs/static/**/*.js")
server.watch("docs/static/**/*.css")
server.watch("docs/static/**/*.png")
server.watch("docs/static/**/*.jpg")
server.watch("docs/photos/*")
server.watch("docs/**/*.html")
server.serve(root="docs")
