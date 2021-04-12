;;;; Prototyping the gui. Nothing is meant to be taken as good coding style, or permanent.
(ql:quickload '(:py4cl2 :clog :parenscript :cl-who))

(py4cl2:initialize)

(py4cl2:defpymodule "phconvert" t :lisp-package "PH")

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
                    (format nil
                            "<script>
                            var editor_~A = ace.edit('~A-body');
                            editor_~A.setTheme('ace/theme/xcode');
                            // editor_~A.session.setMode('ace/mode/lisp');
                            editor_~A.session.setTabSize(3);
                            editor_~A.focus();
                           </script>"
                            id id
                            id id
                            id id)))))

;; bang-on for the above code, minus the <script> tags and assuming id is 5
(ps:ps*
 (let* ((id 5)
        (editor-name (alexandria:symbolicate 'editor_ (format nil "~a" id))))
   `(progn (ps:var ,editor-name (ps:chain ace (edit ,(format nil "~a-body" id))))
           (ps:chain ,editor-name (set-theme "ace/theme/xcode"))
           (ps:chain ,editor-name session (set-tab-size 3))
           (ps:chain ,editor-name (focus)))))

(defun do-ide-file-open (obj)
  (server-file-dialog obj "Open..." "./"
                      (lambda (fname)
                        (when fname
                          (do-ide-file-new obj)
                          (setf (window-title (current-window obj)) fname)
                          (js-execute obj
                                      (format nil
                                              "editor_~A.setValue('~A');editor_~A.moveCursorTo(0,0);"
                                              (html-id (current-window obj))
                                              (escape-string (read-file fname))
                                              (html-id (current-window obj))))))))

;;; copied from tutorial 22
(defun on-help-about (obj)
  (let* ((about (create-gui-window obj
                                   :title   "About"
                                   :content "<div class='w3-black'>
                                         <center><img src='/img/clogwicon.png'></center>
                                     <center>CLOG</center>
                                     <center>The Common Lisp Omnificent GUI</center></div>
                             <div><p><center>Tutorial 22</center>
                                         <center>(c) 2021 - David Botton</center></p></div>"
                                   :hidden  t
                                   :width   200
                                   :height  200)))
    (window-center about)
    (setf (visiblep about) t)
    (set-on-window-can-size about (lambda (obj)
                                    (declare (ignore obj))()))))

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
         (tmp   (create-gui-menu-icon menu :on-click #'on-help-about))
         (win   (create-gui-menu-drop-down menu :content "Window"))
         (tmp   (create-gui-menu-item win :content "Maximize All" :on-click #'maximize-all-windows))
         (tmp   (create-gui-menu-item win :content "Normalize All" :on-click #'normalize-all-windows))
         (tmp   (create-gui-menu-window-select win))
         (dlg   (create-gui-menu-item menu :content "Edit File(s)" :on-click #'do-ide-file-open))
         ;; (tmp   (create-gui-menu-item dlg :content "Server File Dialog Box" :on-click #'on-dlg-file))
         (help  (create-gui-menu-drop-down menu :content "Help"))
         (tmp   (create-gui-menu-item help :content "About" :on-click #'on-help-about))
         (tmp   (create-gui-menu-full-screen menu)))
    (declare (ignore tmp)))
  (set-on-before-unload (window body) (constantly ""))
  (run body))

(defun phui ()
  "Start phui."
  (initialize #'on-new-window)
  (open-browser))
