# файл: pox/ext/controller.py

from pox.core import core, getLogger
import pox.openflow.libopenflow_01 as of
from pox.openflow import openflow

# логгер нашего модуля
log = getLogger("sdn.controller")
log.setLevel("DEBUG")

class LearningSwitch (object):
    def __init__ (self, connection):
        self.connection = connection
        self.mac_to_port = {}
        connection.addListeners(self)

    def _handle_PacketIn (self, event):
        packet = event.parsed
        in_port = event.port
        src, dst = packet.src, packet.dst

        # учим MAC → порт
        self.mac_to_port[src] = in_port
        log.debug("Switch %s: learned %s → port %s",
                  event.connection.dpid, src, in_port)

        if dst in self.mac_to_port:
            out_port = self.mac_to_port[dst]
            log.debug("Forwarding %s → %s out port %s", src, dst, out_port)
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, in_port)
            msg.idle_timeout = 10
            msg.hard_timeout = 30
            msg.actions.append(of.ofp_action_output(port=out_port))
            event.connection.send(msg)
        else:
            log.debug("Unknown dst %s — flooding", dst)
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            msg.in_port = in_port
            event.connection.send(msg)

def launch (port="6633"):
    """
    Запускаем OpenFlow‑слушатель на 0.0.0.0:port и регистрируем
    обработчик ConnectionUp → LearningSwitch.
    Параметр port можно передать через командную строку:

      ./pox.py controller --port=6653
    """
    port = int(port)
    log.info("Starting SDN controller on 0.0.0.0:%s", port)

    # 1) говорим встроенному сервису OpenFlow слушать этот порт
    openflow.listen("0.0.0.0", port)

    # 2) навешиваем обработчик новых подключений
    def start_switch (event):
        log.info("New switch connected: %s", event.connection)
        LearningSwitch(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
