# файл: pox/ext/learning.py

from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class LearningSwitch (object):
    def __init__ (self, connection):
        # connection — объект, связывающий этот контроллер с одним OpenFlow свитчем
        self.connection = connection
        # таблица MAC → порт
        self.mac_to_port = {}

        # подписываемся на событие PacketIn
        connection.addListeners(self)

    def _handle_PacketIn (self, event):
        """
        Обрабатываем приходящий Ethernet‑пакет.
        """
        packet = event.parsed
        in_port = event.port

        src = packet.src
        dst = packet.dst

        # 1) учим, что src видно на in_port
        self.mac_to_port[src] = in_port
        log.debug("Свитч %s: запомним MAC %s → порт %s", 
                  event.connection.dpid, src, in_port)

        # 2) куда флоуить dst?
        if dst in self.mac_to_port:
            out_port = self.mac_to_port[dst]
            log.debug("Форвардим пакет %s → %s на порт %s", src, dst, out_port)
            # создаём правило и сразу же отправляем пакет по нему
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, in_port)
            msg.idle_timeout = 10   # удалить правило через 10 с бездействия
            msg.hard_timeout = 30   # жить не дольше 30 с
            msg.actions.append(of.ofp_action_output(port = out_port))
            event.connection.send(msg)
        else:
            # неизвестный dst — флудим на все порты, кроме входного
            log.debug("MAC %s неизвестен, флудим", dst)
            msg = of.ofp_packet_out()
            msg.data = event.ofp  # оригинальный пакет
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            msg.in_port = in_port
            event.connection.send(msg)


def launch ():
    """
    Точка входа в приложение. Запускается автоматически при ./pox.py learning
    """
    def start_switch (event):
        log.info("Новый свитч подключился: %s", event.connection)
        LearningSwitch(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
