/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2013 GTA, UFRJ, RJ - Brasil
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Author: João Vitor Torres <jvitor@gta.ufrj.br>
 */

#include "ndn-producer-getlsa-nlsrlike.h"
#include "ns3/log.h"
#include "ns3/ndn-interest.h"
#include "ns3/ndn-data.h"
#include "ns3/ndnSIM/utils/ndn-fw-hop-count-tag.h"
#include "ns3/string.h"
#include "ns3/uinteger.h"
#include "ns3/packet.h"
#include "ns3/simulator.h"
#include "ns3/ndn-app-face.h"
#include "ns3/ndn-fib.h"
#include "ns3/buffer.h"
#include "best-route-nlsr-like.h"
#include "ndn-payload-header.h"
#include "ns3/ndn-fib.h"
#include <ns3/ndnSIM/model/ndn-l3-protocol.h>
#include <boost/ref.hpp>
#include <boost/lambda/lambda.hpp>
#include <boost/lambda/bind.hpp>
#include <boost/lexical_cast.hpp>

namespace ll = boost::lambda;

NS_LOG_COMPONENT_DEFINE ("ndn.ProducerGetLSANLSRLike");

namespace ns3 {
namespace ndn {

NS_OBJECT_ENSURE_REGISTERED (ProducerGetLSANLSRLike);
   
TypeId
ProducerGetLSANLSRLike::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::ndn::ProducerGetLSANLSRLike")
    .SetGroupName ("Ndn")
    .SetParent<App> ()
    .AddConstructor<ProducerGetLSANLSRLike> ()
    .AddAttribute ("Prefix","Prefix, for which producer has the data",
                   StringValue ("/"),
                   MakeNameAccessor (&ProducerGetLSANLSRLike::m_prefix),
                   MakeNameChecker ())
    .AddAttribute ("Postfix", "Postfix that is added to the output data (e.g., for adding producer-uniqueness)",
                   StringValue ("/"),
                   MakeNameAccessor (&ProducerGetLSANLSRLike::m_postfix),
                   MakeNameChecker ())
    .AddAttribute ("PayloadSize", "Virtual payload size for Content packets",
                   UintegerValue (1024),
                   MakeUintegerAccessor (&ProducerGetLSANLSRLike::m_virtualPayloadSize),
                   MakeUintegerChecker<uint32_t> ())
    .AddAttribute ("Freshness", "Freshness of data packets, if 0, then unlimited freshness",
                   TimeValue (Seconds (0.05)),
                   MakeTimeAccessor (&ProducerGetLSANLSRLike::m_freshness),
                   MakeTimeChecker ())
    .AddAttribute ("Signature", "Fake signature, 0 valid signature (default), other values application-specific",
                   UintegerValue (0),
                   MakeUintegerAccessor (&ProducerGetLSANLSRLike::m_signature),
                   MakeUintegerChecker<uint32_t> ())
    .AddAttribute ("KeyLocator", "Name to be used for key locator.  If root, then key locator is not used",
                   NameValue (),
                   MakeNameAccessor (&ProducerGetLSANLSRLike::m_keyLocator),
                   MakeNameChecker ())
    ;
  return tid;
}
  
  
ProducerGetLSANLSRLike::ProducerGetLSANLSRLike ()
{
  // NS_LOG_FUNCTION_NOARGS ();
}


// inherited from Application base class.
void
ProducerGetLSANLSRLike::StartApplication ()
{
  NS_LOG_FUNCTION_NOARGS ();
  NS_ASSERT (GetNode ()->GetObject<Fib> () != 0);
  App::StartApplication ();
  NS_LOG_DEBUG ("NodeID: " << GetNode ()->GetId ());
//  Ptr<Fib> fib = GetNode ()->GetObject<Fib> ();
  m_prefix.append ("router");
  m_prefix.appendSeqNum (GetNode ()->GetId ());
  m_prefix.append ("getlsa");
//  Ptr<fib::Entry> fibEntry = fib->Add (m_prefix, m_face, 0);
//  fibEntry->UpdateStatus (m_face, fib::FaceMetric::NDN_FIB_GREEN);
  (GetNode()->GetObject<ns3::ndn::fw::BestRouteNLSRLike> ())
    ->AddFibEntry (m_prefix, m_face, 0);
  RefreshFib();
}

void
ProducerGetLSANLSRLike::RefreshFib ()
{
//  Ptr<Fib> fib = GetNode ()->GetObject<Fib> ();
//  Ptr<fib::Entry> fibEntry = fib->Add (m_prefix, m_face, 0);
//  fibEntry->UpdateStatus (m_face, fib::FaceMetric::NDN_FIB_GREEN);
  (GetNode()->GetObject<ns3::ndn::fw::BestRouteNLSRLike> ())
    ->AddFibEntry (m_prefix, m_face, 0);
  Simulator::Schedule (Seconds (0.1), &ProducerGetLSANLSRLike::RefreshFib, this);
}

void
ProducerGetLSANLSRLike::StopApplication ()
{
  NS_LOG_FUNCTION_NOARGS ();
  NS_ASSERT (GetNode ()->GetObject<Fib> () != 0);
  App::StopApplication ();
}


void
ProducerGetLSANLSRLike::OnInterest (Ptr<const Interest> interest)
{
  //Interest /router/routerid/getlsa/type/lsahash
  //         /router/routerid/getlsa/type/lsahash/npkts/pos/seq
  App::OnInterest (interest); // tracing inside
  if (!m_active) return;

  Ptr<Data> data = Create<Data> ();
  Ptr<Name> dataName = Create<Name> (interest->GetName ());
  NS_LOG_DEBUG (dataName->toUri());
  dataName->append (m_postfix);
  data->SetName (dataName);
  data->SetFreshness (m_freshness);

  data->SetSignature (m_signature);
  if (m_keyLocator.size () > 0)
    {
      data->SetKeyLocator (Create<Name> (m_keyLocator));
    }

  uint32_t lsatype = dataName->get(3).toNumber();
  uint32_t lsahash = dataName->get(4).toNumber();
  Ptr<PayloadHeader> payheader = Create<PayloadHeader> ();
  Ptr<Name> payl = Create<Name> ();
  Name aux = (GetNode()->GetObject<ns3::ndn::fw::BestRouteNLSRLike> ())->GetLSA (lsahash, lsatype);

////////  1111 Edit mtu to change fragmentation
  uint32_t mtu = 1450;
  uint32_t bytes = 2;
  uint32_t dnbytes = 2;
  for (Name::iterator it = aux.begin(); it != aux.end(); it++)
    bytes = bytes + it->size() + 2;
  for (Name::iterator it = dataName->begin(); it != dataName->end(); it++)
    dnbytes = dnbytes + it->size() + 2;
  uint32_t npkts = bytes / (mtu - dnbytes);
  uint32_t nbytespkt = mtu - dnbytes;  

/////////////  1111
  
  if (aux.size() == 0)
  {
    NS_LOG_WARN("LSA not found: " << lsahash << ", string: " << lsahash); 
    payl->append ("no");
  }
  else if (npkts > 1)
  {
  ////////////////////  2222 Treating fragmentation
//    NS_LOG_UNCOND ("Time: " << Simulator::Now ().ToDouble (Time::S) 
//      << ", ProducerGetLSANLSRLike MTU overflow! \t Packets: " << npkts);
    NS_LOG_DEBUG ("Get LSA MTU overflow! \t Packets: " << npkts);
    uint32_t count = 2;
    uint32_t pos = 0;
    uint32_t type =  dataName->get(3).toNumber();
    if (dataName->size() == 5)
    {
      Name::iterator it = aux.begin();
      while (count < nbytespkt && it != aux.end())
      {
        count = count + it->size() + 2;
        payl->append (*it); 
        it++; 
        pos++;       
      }    
      dataName->appendSeqNum (npkts);
      dataName->appendSeqNum (pos);
      dataName->appendSeqNum (0);
    }
    else
    {
      pos = dataName->get(6).toNumber();
      while (count < nbytespkt && pos < aux.size())
      {
        payl->append (aux.get(pos));
        count = count + aux.get(pos).size() + 2;
        pos++;
      }
    }  
    payl->appendSeqNum (pos);  
/////////////////////////    2222

  }
  else
    payl->append (aux.begin(), aux.end()); 
  NS_LOG_DEBUG ("Payload: " << payl->toUri() << ", size: " << payl->size());
//  NS_LOG_UNCOND ("ProducerGetLSANLSRLike Payload: " << payl->toUri() << ", size: " << payl->size());
  payheader->SetPayload (payl);
  Ptr<Packet> packt = Create<Packet> ();
  packt->AddHeader (*payheader);
  data->SetPayload (packt);

  // Echo back FwHopCountTag if exists
  FwHopCountTag hopCountTag;
  if (interest->GetPayload ()->PeekPacketTag (hopCountTag))
    {
      data->GetPayload ()->AddPacketTag (hopCountTag);
    }
  m_face->ReceiveData (data);
  m_transmittedDatas (data, this, m_face);
}

} // namespace ndn
} // namespace ns3
