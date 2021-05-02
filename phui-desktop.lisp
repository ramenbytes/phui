;;;; Prototyping the gui. Nothing is meant to be taken as good coding style, or permanent.
(ql:quickload '(:clog :parenscript :cl-who :serapeum :py4cl))


;; One, use my prefered browser. Two, do it asynchronously.
(setf trivial-open-browser:*browser-function* (lambda (url) (uiop:launch-program (format nil "qutebrowser ~a" url))))

(defpackage #:phui
  (:use #:cl #:clog #:clog-gui)         ; For this tutorial we include clog-gui
  (:export #:phui #:shutdown)
  (:import-from #:serapeum
                #:dict))

(in-package :phui)

(py4cl:import-function "convert" :from "phui.unified_conversion")

(serapeum:toggle-pretty-print-hash-table)

;;; copied from demo 3
(defun read-file (infile)
  (with-open-file (instream infile :direction :input :if-does-not-exist nil)
    (when instream
      (let ((string (make-string (file-length instream))))
        (read-sequence string instream)
        string))))

(defun do-ide-file-new (obj)
  (let* ((win (create-gui-window obj :title "New window"
                                     :height 400
                                     :width 650))
         (id (html-id win))
         (editor-name (alexandria:symbolicate 'editor_ (princ-to-string id))))
    (set-on-window-size win (lambda (obj)
                              (js-execute obj (ps:ps* `(ps:chain ,editor-name (resize))))))
    (set-on-window-size-done win (lambda (obj)
                                   (js-execute obj (ps:ps* `(ps:chain ,editor-name (resize))))))
    (create-child win
                  (cl-who:with-html-output-to-string (out)
                    (:script
                     (cl-who:str
                      (ps:ps* `(progn (ps:var ,editor-name (ps:chain ace (edit ,(format nil "~a-body" id))))
                                      (ps:chain ,editor-name (set-theme "ace/theme/xcode"))
                                      ;; (ps:chain ,editor-name session (set-mode "ace/mode/lisp"))
                                      (ps:chain ,editor-name session (set-tab-size 3))
                                      (ps:chain ,editor-name (focus))))))))))

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
                                   :title "About"
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

(defun do-convert (obj)
  (server-file-dialog obj "Convert" (uiop:getcwd)
                      (lambda (fname)
                        (when fname
                          ;; (setf (window-title (current-window obj)) fname)
                          (let ((output-lines (serapeum:lines
                                               (with-output-to-string (*standard-output*)
                                                 (convert
                                                  "/home/vir/weisslab/phui/data/0023uLRpitc_NTP_20dT_0.5GndCl.sm"
                                                  :data_fragment (dict "description" "hi")))))
                                (win (create-gui-window
                                      obj :title "Output"
                                      :content
                                      (who:with-html-output-to-string (out)
                                        (:div :class "w3-black"
                                              (loop for line in output-lines
                                                    with first? = t
                                                    do (cond (first? (setf first? nil) (who:str line))
                                                             (t (who:htm (:p (who:str line))))))))
                                      :hidden  t)))
                            (window-center win)
                            (setf (visiblep win) t))))))

(defmacro indirectly (function-name)
  "Simple macro that wraps the named function in a lambda, so that we can deal
with a function object (the lambda) while still being able to pick up
redefinitions of the named function."
  `(lambda (&rest args)
     (apply #',function-name args)))

(defun on-new-window (body)
  (setf (title (html-document body)) "Phconvert User Interface")
  (clog-gui-initialize body)
  ;; This is the Ace js code editor. This cdn works for most, if fails (getting
  ;; New as a blank window,etc) you can cd clog/static-files/ and run
  ;; git clone https://github.com/ajaxorg/ace-builds/
  ;; and uncomment this line and comment out the next:
  ;; (load-script (html-document body) "/ace-builds/src-noconflict/ace.js")
  (load-script (html-document body) "https://pagecdn.io/lib/ace/1.4.12/ace.js")
  (add-class body "w3-cyan")  
  (let* ((menu  (create-gui-menu-bar body))
         (tmp   (create-gui-menu-icon menu :on-click (indirectly on-help-about)))
         (win   (create-gui-menu-drop-down menu :content "Window"))
         (tmp   (create-gui-menu-item win :content "Maximize All" :on-click (indirectly maximize-all-windows)))
         (tmp   (create-gui-menu-item win :content "Normalize All" :on-click (indirectly normalize-all-windows)))
         (tmp   (create-gui-menu-window-select win))
         (dlg   (create-gui-menu-item menu :content "Edit File(s)" :on-click (indirectly do-ide-file-open)))
         (dlg   (create-gui-menu-item menu :content "Convert Files" :on-click (indirectly do-convert)))
         ;; (tmp   (create-gui-menu-item dlg :content "Server File Dialog Box" :on-click 'on-dlg-file))
         (help  (create-gui-menu-drop-down menu :content "Help"))
         (tmp   (create-gui-menu-item help :content "About" :on-click (indirectly on-help-about)))
         (tmp   (create-gui-menu-full-screen menu)))
    (declare (ignore tmp)))
  (set-on-before-unload (window body) (constantly ""))
  (run body))

(defun phui ()
  "Start phui."
  (initialize #'on-new-window)
  (open-browser))
