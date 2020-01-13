# coding=utf-8

message_stings = {
    'first_start_message': 'Здраствуйте {}, давайте начнем.\n'
                           'Для начала отправьте мне ваше Фамилию и Имя.\n'
                           'Например Петров Петя',
    'start_message': 'Здраствуйте {}, чтобы участвовать в соревновании, вам нужно сделать упражнения, '
                     'которые вы можете получить отправив команду /get_exercise или нажать на кнопку ниже.\n\n'
                     'Если вы сделали все упражнения отправьте свой результат отправив команду /send_result или '
                     'нажать на кнопку ниже.',
    'ask_exercise': 'Какие упражнения вы хотите опубликовать на {}',
    'sure_to_publish': 'Вы уверены, что хотите опубликовать эти упражнения на {0}?\n\n{1}\n\n'
                       'После, вы не их зможете изменить.',
    'wrong_name': 'Похоже, вы отправили только имя, пожалуйста, отправьте заново ваше Имя и Фамилию',
    'message_wait': 'Пожалуйста, подождите...',
    'name_saved': '{}, информация о вас успешна сохранена.\nВы можете использовать бот',
    'successfully_saved': 'Упражнения успешно сохранены. Для проверки отправьте команду /get_exercise',
    'results_successfully_saved': 'Ваш результат и видео успешно сохранены\n\n'
                                  'Вы сделали упражнение за {0}\n'
                                  'Ваше видео: [Ссылка на видео]({1})',
    'something_wrong': 'Что то пошло не так, не удалось сохранить данные в БД\n[ERROR] {}',
    'ask_to_send': 'Вы хотите отправить сообщение всем или только нескольким пользователям?',
    'what_to_send_everyone': 'Что вы хотите отправить всем пользователям?',
    'list_users': 'Все ваши пользователи ↙️\n       User ID            Имя пользователя.\n{}',
    'ask_users_id': 'Отправьте через запятую User ID пользователей, которым вы хотите отправить сообщение.\n'
                    'Например: 11111111, 33333333, 55555555',
    'rejected': 'Вы отменили действия',
    'if_not_reject': 'Если вы все посмотрели результаты, отправьте команду /start или нажмите кнопку Отменить.',
    'no_user': 'Пользователя в вашей базе с User ID: {} нет',
    'no_sent_users': 'В нашей базе не нашлось ни одного пользователя с этими User ID: {}',
    'choose_correct_action': 'Выберите правильное действие!',
    'send_video_state': 'Вы решили опубликовать видео, ваше время {0}.\n'
                        'Длительность вашего видео не должно быть меньше этого времени: {1}',
    'ask_what_to_send': 'Что вы хотите отправить своим пользователям?',
    'send_exercise': 'Вот список упражнений на {}',
    'no_exercise': 'Похоже, еще не опубликовали упражнения на {}, попробуйте позже.',
    'no_exercise_to_compete': 'Похоже, еще не опубликовали упражнения на {}, соответственно нету участников',
    'correct_time': 'Вы сделали упражнение за {} или {}?',
    'no_competitors': 'Еще никто не участвовал в этом соревновании',
    'later': 'Ваш результат {} опубликован, но без видео. Чтобы добавить видео, нажмите на кнопку "Отправить видео"',
    'incorrect_video': 'Вы отправили не то видео, вы сделали упражнение за {0}, а ваше видео длиной {1}.\n'
                       'Пожалуйста, попробуйте заново и отправьте правильное видео!',
    'send_video': 'Ваше время {0}, если вы отправли свой результат верно, отправьте видео как докозательство того, '
                  'что вы сделали упражнеине за это время - {1} \n\n'
                  'Если вы отправили результат неверно, нажмите на кнопку Отменить или /start, '
                  'затем отправьте свое время заново.\n\n'
                  'Если у вас на данный момент нет видео, отправьте команду /later.\n'
                  'Когда будет видео, нажмите на кнопку "Отправить видео"',
    'wrong_time': 'Вы отправили неверное вермя, пожалуйтса, отправьте свой результат в виде Минуты:Секунды\n'
                  'Например, 5:45 или 8:16',
    'time_latter': 'Отправленное ваше время {} содержат буквы, отправьте правильное время в виде Минуты:Секунды\n'
                   'Например, 5:45 или 8:16',
    'exercise_done': 'Вы сделали упражнения на {0}. Ваше упражнение:\n\n{1}\n\n'
                     'Пожалуйста, отправьте свой результат в виде Минуты:Секунды.\n'
                     'Например 5:45 или 10:16\n'
                     'Будьте внимательны! Отправив свой результат, вы не сможете его изменить в будущем.',
    'is_admin_sure': 'Вы уверены, что хотите отправить это сообщение пользователям?\n'
                     'Оно будет выглядеть так\n\n{}',
    'what_to_send_some': 'Что вы хотите отправить пользователям по имени ↙️\n\n{}',
    'admin_string': '/get_users_count - Получить количество пользователей\n\n'
                    '/send_everyone - Отрпавить сообщение всем рользователям\n\n'
                    '/get_deleted_count - Получить количество пользователей, которые удалили бота\n\n'
                    '/publish_exercise - Опубликовать упражнения на сегодня',
}