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

#ifndef NDN_PRODUCER_GETLSA_NLSRLIKE_H
#define NDN_PRODUCER_GETLSA_NLSRLIKE_H

#include <ns3/ndnSIM/apps/ndn-app.h>
#include "ns3/ptr.h"
#include "ns3/ndn-name.h"
#include "ns3/ndn-data.h"
#include <boost/functional/hash.hpp>

namespace ns3 {
namespace ndn {

class ProducerGetLSANLSRLike : public App
{
public: 
  static TypeId
  GetTypeId (void);
        
  ProducerGetLSANLSRLike ();

  // inherited from NdnApp
  void OnInterest ( Ptr<const Interest> interest);
  
  void RefreshFib();  

protected:
  // inherited from Application base class.
  virtual void
  StartApplication ();    // Called at time specified by Start

  virtual void
  StopApplication ();     // Called at time specified by Stop

private:
  Name m_prefix;
  Name m_postfix;
  uint32_t m_virtualPayloadSize;
  Time m_freshness;

  uint32_t m_signature;
  Name m_keyLocator;
  boost::hash<std::string> string_hash;
};

} // namespace ndn
} // namespace ns3

#endif // NDN_PRODUCER_GETLSA_NLSRLIKE_H
