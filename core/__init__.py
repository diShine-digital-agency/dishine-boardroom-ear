# Intentionally left empty.
#
# Eagerly re-exporting ``BoardroomEar`` here would force every import of the
# ``core`` package to load ``faster-whisper`` — which breaks ``--help`` and
# ``--health-check`` before the user has installed the heavy dependencies.
# Import submodules directly: ``from core.boardroom_ear import BoardroomEar``.
