;;;; Prototyping the gui. Nothing is meant to be taken as good coding style, or permanent.
(ql:quickload '(:py4cl2 :clog :parenscript :cl-who))


;; One, use my prefered browser. Two, do it asynchronously.
(setf trivial-open-browser:*browser-function* (lambda (url) (uiop:launch-program (format nil "qutebrowser ~a" url))))

(defpackage #:phui
  (:use #:cl #:clog #:clog-gui)         ; For this tutorial we include clog-gui
  (:export phui))

(in-package :phui)

;;; copied from demo 3
(defun read-file (infile)
  (with-open-file (instream infile :direction :input :if-does-not-exist nil)
    (when instream
      (let ((string (make-string (file-length instream))))
        (read-sequence string instream)
        string))))

(defun do-ide-file-new (obj)
  (let ((win (create-gui-window obj :title "New window"
                                    :height 400
                                    :width 650)))
    (set-on-window-size win (lambda (obj)
                              (js-execute obj (format nil "editor_~A.resize()" (html-id win)))))
    (set-on-window-size-done win (lambda (obj)
                                   (js-execute obj (format nil "editor_~A.resize()" (html-id win)))))
    (create-child win
                  (let ((id (html-id win)))
                    (cl-who:with-html-output-to-string (out)
                      (:script
                       (cl-who:str
                        (ps:ps* (let* ((editor-name (alexandria:symbolicate 'editor_ (format nil "~a" id))))
                                  `(progn (ps:var ,editor-name (ps:chain ace (edit ,(format nil "~a-body" id))))
                                          (ps:chain ,editor-name (set-theme "ace/theme/xcode"))
                                          (ps:chain ,editor-name session (set-mode "ace/mode/lisp"))
                                          (ps:chain ,editor-name session (set-tab-size 3))
                                          (ps:chain ,editor-name (focus))))))))))))

(defun do-ide-file-open (obj)
  (server-file-dialog obj "Open..." "./"
                      (lambda (fname)
                        (when fname
                          (do-ide-file-new obj)
                          (setf (window-title (current-window obj)) fname)
                          (js-execute obj
                                      (let ((editor-name (alexandria:symbolicate 'editor_ (princ-to-string (html-id (current-window obj))))))
                                        (ps:ps* `(ps:chain ,editor-name (set-value ,(read-file fname)))
                                                `(ps:chain ,editor-name (move-cursor-to 0 0)))))))))

;;; copied from tutorial 22
(defun on-help-about (obj)
  (let* ((about (create-gui-window obj
                                   :title   "About"
                                   :content
                                   (who:with-html-output-to-string (out)
                                     (:div :class "w3-black"
                                           (:center "Phui")
                                           (:center "Phconvert User Interface")
                                           (:center "2021 - Donald Ferschweiler")
                                           (:center (:img :src "/img/clogwicon.png"))
                                           (:center "Prototyped with CLOG")
                                           (:center "The Common Lisp Omnificent GUI")
                                           (:center "Tutorial 22")
                                           (:center "2021 - David Botton")))
                                   :hidden  t
                                   :width   300
                                   :height  210)))
    (window-center about)
    (setf (visiblep about) t)
    (set-on-window-can-size about (lambda (obj)
                                    (declare (ignore obj))()))))

(defun on-new-window (body)
  (setf (title (html-document body)) "Tutorial 22")  
  (clog-gui-initialize body)
  ;; This is the Ace js code editor. This cdn works for most, if fails (getting
  ;; New as a blank window,etc) you can cd clog/static-files/ and run
  ;; git clone https://github.com/ajaxorg/ace-builds/
  ;; and uncomment this line and comment out the next:
  ;; (load-script (html-document body) "/ace-builds/src-noconflict/ace.js")
  (load-script (html-document body) "https://pagecdn.io/lib/ace/1.4.12/ace.js")
  (add-class body "w3-cyan")  
  (let* ((menu  (create-gui-menu-bar body))
         (tmp   (create-gui-menu-icon menu :on-click 'on-help-about))
         (win   (create-gui-menu-drop-down menu :content "Window"))
         (tmp   (create-gui-menu-item win :content "Maximize All" :on-click 'maximize-all-windows))
         (tmp   (create-gui-menu-item win :content "Normalize All" :on-click 'normalize-all-windows))
         (tmp   (create-gui-menu-window-select win))
         (dlg   (create-gui-menu-item menu :content "Edit File(s)" :on-click 'do-ide-file-open))
         ;; (tmp   (create-gui-menu-item dlg :content "Server File Dialog Box" :on-click 'on-dlg-file))
         (help  (create-gui-menu-drop-down menu :content "Help"))
         (tmp   (create-gui-menu-item help :content "About" :on-click 'on-help-about))
         (tmp   (create-gui-menu-full-screen menu)))
    (declare (ignore tmp)))
  (set-on-before-unload (window body) (constantly ""))
  (run body))

(defun phui ()
  "Start phui."
  (initialize #'on-new-window)
  (open-browser))
