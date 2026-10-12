"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/31b3720044ca458d90461a4ba5a22abf/part_008.stl', 'relative_path': '31b3720044ca458d90461a4ba5a22abf/part_008.stl', 'source_sha256': '1545b1152597a904c3c91857d0f730ab1820bb8af694bfa265e6580379989b43', 'input_faces': 304, 'input_vertices': 172, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1168203055858612, -0.14806285500526428, 0.17689917981624603], [0.14851191639900208, -0.11019756644964218, 0.21729272603988647]]}
GEOMETRY_BASE85 = 'c$}q~2~-qE9>!bLM59qqOz<92ITZ00FLdIGCwLn*0xAkB9)NhFt;Q%|5CufJG6)KaIW(HYgU}ukbaEJ?z9lhAlFcca?B>v{akE|ZeNDReW#8MkJMY!|e*ce}fBmbvyJ}_#8CSQSyMk8-rQ4Sat~gv3MYP6>yAmG}6Bji<BG!M|inVnVSLutFp=lGRO$d3mjuNk|_g)YYJ3q#Ipv`;m!v5ZVHt&VYW8z}MmxV5mSr8%oQQ=EtBXmDDGJHjZ9{cnR=;deY?dxYtu>Fs(C-f53@4qe`s;m9fkLSyTMwDC;v6}nD+tT-cUHa<7Z0S3GYAt<7z;XE1?^K9b@#-mkHMWWLl_!g&uPS}f|M=Z=GQWCK`r6%o(yv~;2IJ;`g*>11NB??G^q+KE`e7#rBmeYb=__fkOW&3-O!{FvcSv6wbO8BB1R+oKO8CRJOW)ppJjSg%Px|VbMbdZt8jL)?bJ72!;i%usRg>@gw5_aDJ9rHFn>Ulb+U61RG(Cs<>$po_TU~`Zzq^QW@3nw``3>an`ZoGkdPv{)OD6JMJBs`#TT8#XdK2<g?m_>8wwiffcDEShPi>DpY0>cK2P03^C#W<0v$Mi?Z0cGr^Z0y@dZs*GD*Wo}A6=4pIy{oTveOOzvBR>zdbYzk+5g@1@be4N|7f7}9eF+8mh~^4h<c8#l)mlGB~6ao`wqrkyBhxe+tRlm@JF5Y1nJvTJm8PaN1lL<(pT#K3jgzXT$fHN`n#k`Uwf|{{abHF|HS%o9c&veW8B}jN<YlQP5O=>4_JIH=?$4jSssZzHQS_L9UcJxQr2ZTZq;__tEXFGom09vW&hG7^l#M_{!fi?y-p;f|GG-#sj<oaT4oB??XlVL=Ny&Kmlm0Z_4#rv?vqXT@jQm6qyB<P$UkQ>>KvYlJmE9ZKYE_bulCrFJUx?<|6ma6@y<e>53p`_rSqTq%9JI@@1BGFH`AoA&K&DB`?jz4p#P(2j9VuUdA5Ft>z+KK-0a(yzJ&h$>LdRH`1WV>QBT`si|?4{z_^*dPD}qCIp|-KDt+Z<KKftWg6HLGNA$m3fOXsartEL)Qd4gBZ5Lic{@pL*x|9_nf5d6j>04M~_HF4WG48R(nD6!@=zrFUJf|+8o{c5wKjAR0SA%vIUzv6T^?dYkx!E_?%^v>%_e0!K`2DL;5BEKF@Nwi%sDVG`1JvVt!t%VRjjorQ{jfnlBLB5}GQZt+67~P^59C?!R)yJj{E9r<o1<`_)O!o{ys2QFlR`1CZ%(70u1&Fz4ZRBg`dQ2KQafMz+TY!A-(LA1^L3V@&b+o*x18gcZ`uXStEM~h=Uzhoq>C6gWdQ04{I1;WJ6`XL{2{*~zxodHuODPRFD6|<{;bLHgX&uRu*&fmciwT_S3yqXPo08sdn8tveeGxn>fhpq`^xhJ<oO5A9W5fN!t5L8k<z>)=G*cr*3G#H{<)DB-|_VV<PYucH2X##EoLw3d{l{g5|_b$YLdk_&I|QS9Q@ATqJPakjQhoH%&TDy{6p7}$3sIs`|jiZdG{*n3Cxh|ti(RVdQMHjep~Mc+=o%WVO}Ge<2=nhi2E??k)^+JebouSW4>3jrC(io9(lfRa9*zG?z5=px`z6j*rczt-z3kwurtN7zjn$;`u3ZFmh(%^?J9joms8TOJ-^cZq;EU<IO_cQQ(Ujvy)f=KePw=IVi)Wutp-S6`*;b)y<I8uYpw$^?&(3u6BUp9&}XUi)#6iS(x2$SxYy#4C-}bf?H}xy=Z>~10d<aVZ#gg2`bo&YIvCIOE2EL;H~7^<rdjuM`u3oymi=G-b|=R5oN3wT4d3QB!?Mq7H&WmqpKsmI-`j;cix(h|SCYlA?Vs=CH2e1V!_fc4F8F!rSm*Nfmd_7{uQrRb?AuC42F5*+0KZp3g~k73jb-1~=48Wfv<vlIIFE6s<lz3v&a&*!hF^U-!?HgsV{=hI&m&`hR$3oGe&;C5=M&Yf0QJB7s%78S{#l6i8B=Q6Zw)_e@>$D%ZurLM7GpnGe?EwM`juJs^ID&umyC1SUR8|zk6%Q8V?Qq~!F;)&7|*Za8=q&4ecpcLWlMkK`K|RE-om&ytI91t&oyKJSMp!MyzW+GUdH~P`6}vEms|D$d&+CLUW=AkKEJ7vC(xhgU2Q#~C$Y}g9-%+a3&S_gJNvAMcuuFifjsAaN1eubG2j%|^O;oad$-G+W?!4W-THaY>kQV-^{?2kjQxau*tac^XR?dM*E+ab&K<SwS=4#sY4jhkqr&VP=c#e-C=bez-|l_Rygr6sJ;n?9+jt_+Jq>lb`B~2$`bvNg>W}nyntl6}&X#jW`{ca!eyF*HJe3#Fzi~@^Pdu>VirKeS^|YK*hVS^ihvl473o79Iue5%@Sn@vnfk~F{7fSGlScfn6Th1xf_d4b~ssPvb&MNFzPyWU7oYsDi_}j;r*X%PGm)|4ow{Bwnd2ZT0%P?Q(Ez9#|d|yys{S5xx>lpXZ6R30ccc|azXWT!Dzo5=ZcQEc(50QtT|Ft1^ab41H;CdAm;ymqp59@i*1^()A+z;<RfZw1S>a6m_bFsqZf*hBhXH>Vg&Y>ZeUpJbMjvJ~q(TCJqL&aTL7;gG$Lzv=a=%4?z5!L6v`e~zgk3RqJPaBQ&8pQ7#&DjJuqc$WrBfC)>klo0x)W^xL<fhce$W6&jsP)KA$WK!1l7%)V@6cO>xE|Ej<o0^=*V`tx1N08+El+P9sjbLQvwsU}d$Q1WWT7p|Ey&{Xdg$#bj@_DUqq>uA<W|&{<d)3aime^%=}3N-P4FDHcC1VIo7s0W=hl&P-EQjNo}Os={M&Z&X1093{~$S!noG_ji}eoUTF<5KAkQVwqvn!xnQI=K;Q72Rp{y&E-T`X9X&#$R>oA92D6iRkY76pw@;s`$X<T>K=+0|1m+E1v--GiDBS%nMo91fcdf0f)@;DcN*5%Kd1PAMFg5I9d+a$(<Ll_Gl$5?O>W5FXB3m(E)@Ic0b`!E*Vow499j0O8L7TlGw;2w+x_hT%0Fk``X#)3yN7Ce^mGo0U8@*cgV>uo)CFIi{?S!gO*XcAfI^JJkL$U@`ELRXT7Mw5juCJT)u3ymTRT}BofOBT9@EOaAT=nG__JIOma&-I*pFylSsbm}B>I(aWOguIuWK^;fVAg5A;$f@Kc>IiZY`FZLP^7G^k)Pdv;<alZyay)q@wL5twIhxvq98F$K^(8MRM^d|zBgs+J9^@$UGHO5aGIA_+FgcdIhH59TA#bFPB5x$WKpjhdfxMGCfjoiNQt))W&CuH{wwd&1GA?F&iQY?$3)uG4+s}9g+jM$adRw5kUDR;$EXKvuEYnz7%$3EyM&1I(yO?JN-#d%(EP8@d^tMQEov5A3#vBGvOUQ@yR;V{0swdf43vcQGve4dSp<ZNfavMc_BvO>N9J@2Q6SWPw6WNpMMfPG|PqyBy$A>(dP4IJUy;+y=x3ce6&Q0)(>{mh^Ko;!?|NbI*E87vi|1i0bdWc*|7VEu`YrU45LS9RDP!Ew0F_(i)aFO!I{Zv9NA{Vhw3G3WyT8HQ8?dLTsqI#2y$PQ{7)3|L|V;f$ZwbTx#`a5ub3(1S9olSG?#P#UJYbJQK-iGUKnBK-S7CeQq;AxBnPh~84GGoCL84Di6Snx>3f`>8|JczNuLIbEh$$n(vbz>~J7h}PF84K>uSa2ZYVVqwed5hi>74d&P=x(ymePp3IWTDw)p_yc%X=I_vWTD&0LKDbBSCfUtk%cZN3td7Mx|A$*1zBheS?DUV&~@Z>oTtjUk7m4uoJbu{P9*Q9P9g6m@1ss5?<40>r;>BX+0@D8Y;q=bA~}<sMjb;=BPUZwl9S2Xs6)xy$O+Uz<OK3+Y5;jPIgZ+s97kSG^&>AQFQIlLFCj0b_98DOub}oNuOP=z`;%kHtEhqGRpfQl;pE}GmV)c+%|-d+Rfk^4xH>NGb^p`9_WyXP;tiI6^#A)itzVnX@4Thws{IljGOoV(?x+{zB0sQHiElm1zW~%K^sN'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
