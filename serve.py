import livereload

import build
import build_photos


def rebuild_blog():
    build.main()


def rebuild_photo():
    build_photos.main()


server = livereload.Server()
server.setHeader("Cache-Control", "no-store")
server.watch("srcs/*.md", rebuild_blog)
server.watch("photos/*.md", rebuild_photo)
server.watch("docs/static/**/*.js")
server.watch("docs/static/**/*.css")
server.watch("docs/static/**/*.png")
server.watch("docs/static/**/*.jpg")
server.watch("docs/photos/*")
server.watch("docs/**/*.html")
server.serve(root="docs")
